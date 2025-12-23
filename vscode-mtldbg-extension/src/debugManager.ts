import * as vscode from 'vscode';

import { ChildProcess, spawn } from 'child_process';
import { randomUUID, UUID } from 'crypto';
import { EventEmitter } from 'events';
import { DebuggerCommandType, DebuggerResponseType, DebuggerRequestIPC, DebuggerResponseIPC, VariableType } from './sharedTypes';

const MINIMUM_RESPONSE_LENGTH = 48;
const MTL_TO_DAP_ID = '00000000-0000-0000-0000-000000000000';

interface PlayerFrame {
    stateNameOrId: string;
    fileName: string;
    lineNumber: number;
}

interface MugenVariable {
    name: string;
    value: number;
}

export class MTLDebugManager extends EventEmitter {
    private _debuggingProcess: ChildProcess | null = null;
    private _incomingMessages: DebuggerResponseIPC[] = [];

    private _partialMessage: Buffer | null = null;

    public async connect(python: string, database: string, mugen: string, stopOnEntry: boolean | undefined) {
        // check if debugger is already running
        if (this._debuggingProcess != null) {
            throw "Debugger has already been launched, please stop any debugging processes before running.";
        }

        // run mtldbg and store the debugging process
        // we need to pass `-i` for IPC-over-stream mode, this will make it possible to communicate with
        // the debugger process via stdin/stdout.
        console.log(`${python} -m mtldbg -d ${database} -m ${mugen} -i`)
        this._debuggingProcess = spawn(python, ["-m", "mtldbg", "-d", database, "-m", mugen, "-i"], {
            stdio: 'pipe'
        });
        this._debuggingProcess.on('error', (err) => {
            console.error('Failed to start child process:', err);
        });
        console.log(`Launched debugger process: ${this._debuggingProcess.pid}`);
        this._debuggingProcess.stdout?.on('data', chunk => {
            if (this._partialMessage) {
                this._partialMessage = Buffer.concat([this._partialMessage, chunk]);
            } else {
                this._partialMessage = chunk;
            }
            this.readMessageFromPartial();
        });
        
        // notify debugger of launch
        const launchResult = await this.sendMessageAndWaitForResponse(DebuggerCommandType.LAUNCH, "");
        if (launchResult.response !== DebuggerResponseType.SUCCESS) {
            this.displayResponseError(launchResult);
            await this.disconnect();
            return;
        }
        // run CONTINUE if the debugger should not stop on entry
        if (!stopOnEntry) {
            const continueResult = await this.sendMessageAndWaitForResponse(DebuggerCommandType.CONTINUE, "");
            if (continueResult.response !== DebuggerResponseType.SUCCESS) {
                this.displayResponseError(launchResult);
                await this.disconnect();
                return;
            }
        }
    }

    public async disconnect() {
        // send `stop` and `exit` commands to the debugging process
        if (this._debuggingProcess && this._debuggingProcess.pid) {
            console.log("Attempting to gracefully stop debugging.");
            const stopResult = await this.sendMessageAndWaitForResponse(DebuggerCommandType.STOP, "");
            const exitResult = await this.sendMessageAndWaitForResponse(DebuggerCommandType.EXIT, "");
            if (stopResult.response === DebuggerResponseType.EXCEPTION) {
                console.log("There may have been an issue when shutting down the debugger, check the result log.");
                this.displayResponseError(stopResult);
            }
            if (exitResult.response === DebuggerResponseType.EXCEPTION) {
                console.log("There may have been an issue when shutting down the debugger, check the result log.");
                this.displayResponseError(stopResult);
            }
            this._debuggingProcess.kill();
        }

        // clean up
        this._debuggingProcess = null;
        this._incomingMessages = [];
        this._partialMessage = null;
    }

    public async continue() {
        if (!this.isConnected()) throw "Can't continue when the debugger is not running!";

        const result = await this.sendMessageAndWaitForResponse(DebuggerCommandType.CONTINUE, "");
        if (result.response !== DebuggerResponseType.SUCCESS) {
            this.displayResponseError(result);
        }
    }

    public async pause() {
        if (!this.isConnected()) throw "Can't pause when the debugger is not running!";

        const result = await this.sendMessageAndWaitForResponse(DebuggerCommandType.IPC_PAUSE, "");
        if (result.response !== DebuggerResponseType.SUCCESS) {
            this.displayResponseError(result);
            return;
        }
    }

    public async requestPlayerList(): Promise<{ name: string, id: number }[]> {
        if (!this.isConnected()) return [];

        const results = await this.sendMessageAndWaitForResponse(DebuggerCommandType.IPC_LIST_PLAYERS, { includeEnemy: true });
        if (results.response !== DebuggerResponseType.SUCCESS) {
            // for player_list we can swallow the game initialization and player initialization errors
            // (because the breakOnEntry will occur before initialization)
            if (results.detail === 'DEBUGGER_GAME_NOT_INITIALIZED' || results.detail === 'DEBUGGER_PLAYERS_NOT_INITIALIZED') {
                console.log(`Requested player list before initialization completed: ${results.detail}`);
            } else {
                this.displayResponseError(results);
            }
            return [];
        }

        return JSON.parse(results.detail);
    }

    public async requestPlayerDetails(player: number): Promise<{ name: string, id: number, frame: PlayerFrame }> {
        if (!this.isConnected()) throw "Cannot request player details when debugger is not connected!";

        const results = await this.sendMessageAndWaitForResponse(DebuggerCommandType.IPC_GET_PLAYER_INFO, { player });
        if (results.response !== DebuggerResponseType.SUCCESS) {
            if (results.detail === 'DEBUGGER_PLAYER_WRONG_TEAMSIDE') {
                console.log(`Requested player list before initialization completed: ${results.detail}`);
            } else {
                this.displayResponseError(results);
            }
            return { name: "", id: 0, frame: { fileName: "", stateNameOrId: "", lineNumber: 1 }};
        }

        return JSON.parse(results.detail);
    }

    public async getPlayerVariables(player: number, type: VariableType): Promise<MugenVariable[]> {
        if (!this.isConnected()) throw "Cannot request variable details when debugger is not connected!";

        const results = await this.sendMessageAndWaitForResponse(DebuggerCommandType.IPC_GET_VARIABLES, { player, type: VariableType[type] });

        if (results.response !== DebuggerResponseType.SUCCESS) {
            this.displayResponseError(results);
            return [];
        }

        return JSON.parse(results.detail);
    }

    public async getPlayerTeamside(player: number): Promise<number> {
        if (!this.isConnected()) throw "Cannot request player information when debugger is not connected!";

        const results = await this.sendMessageAndWaitForResponse(DebuggerCommandType.IPC_GET_TEAMSIDE, { player });

        if (results.response !== DebuggerResponseType.SUCCESS) {
            this.displayResponseError(results);
            return 2;
        }

        return JSON.parse(results.detail).teamside;
    }

    public isConnected() {
        return this._debuggingProcess != null;
    }

    private displayResponseError(response: DebuggerResponseIPC) {
        if (response.response === DebuggerResponseType.EXCEPTION) {
            vscode.window.showErrorMessage(`An error occurred inside the debugger while handling a ${DebuggerCommandType[response.command]} command: ${response.detail}`);
        } else {
            vscode.window.showErrorMessage(this.getDetailedError(response.command, response.detail));
        }
    }

    private getDetailedError(command: DebuggerCommandType, detail: string): string {
        switch(detail) {
            case 'DEBUGGER_HELD_OPEN':
                return "The MUGEN process was still open when exit was requested, and may have become stuck.";
            case 'DEBUGGER_NOT_RUNNING':
                return `The MUGEN process was not running, so the debugger could not handle the ${DebuggerCommandType[command]} command.`;
            case 'DEBUGGER_UNRECOGNIZED_COMMAND':
                return `The command ${DebuggerCommandType[command]} was not recognized by the debugger, maybe the mtldbg and extension versions are out of sync?`;
            case 'DEBUGGER_GAME_NOT_INITIALIZED':
                return "The game offsets for MUGEN are not yet initialized.";
            case 'DEBUGGER_PLAYERS_NOT_INITIALIZED':
                return "The player offsets for MUGEN are not yet initialized.";
            case 'DEBUGGER_INVALID_INPUT':
                return "An invalid input was provided for an IPC command (this is probably the extension developer's fault)";
            case 'DEBUGGER_ALREADY_PAUSED':
                return "The debugger has already been paused by another request.";
            case 'DEBUGGER_PLAYER_NOT_EXIST':
                return "Player data was requested for a player ID which does not exist (this is probably the extension developer's fault)";
            case 'DEBUGGER_PLAYER_WRONG_TEAMSIDE':
                return "Player data was requested for a player on the enemy's team (cannot display source files for enemy players)";
            case 'DEBUGGER_PLAYER_INVALID_STATE':
                return "Player data was requested for a player which is in an invalid state number.";
        }

        return "Unknown error";
    }

    private readMessageFromPartial() {
        if (this._partialMessage && this._partialMessage.length >= MINIMUM_RESPONSE_LENGTH) {
            // get the next message ID
            const nextMessage = Buffer.from(this._partialMessage.subarray(0, 36));

            const inboundMessageId = new TextDecoder().decode(nextMessage);
            console.log(`Receive response on messageId ${inboundMessageId}`);

            const argumentsBuffer = Buffer.from(this._partialMessage.subarray(36, 48));
            const commandType = argumentsBuffer.readInt32LE(0) as DebuggerCommandType;
            const responseType = argumentsBuffer.readInt32LE(4) as DebuggerResponseType;
            const paramsLength = argumentsBuffer.readInt32LE(8);

            if (this._partialMessage.length < (MINIMUM_RESPONSE_LENGTH + paramsLength)) {
                console.log(`Partial response for ${inboundMessageId} incomplete, will resume read later`);
                return;
            }

            const params = new Uint8Array(this._partialMessage.subarray(48, 48 + paramsLength)).slice();

            console.log(`Received new message with messageId ${inboundMessageId}, command ${commandType}, response ${responseType}`);
            if (inboundMessageId === MTL_TO_DAP_ID) {
                // this is a message from the debugger which needs to trigger behaviour in the adapter, forward it to the
                // debugging session.
                console.log(`Forward event ${DebuggerCommandType[commandType]} to session`);
                this.emit(DebuggerCommandType[commandType], {
                    messageId: inboundMessageId,
                    command: commandType,
                    response: responseType,
                    detail: new TextDecoder().decode(params)
                });
            } else {
                this._incomingMessages.push({
                    messageId: inboundMessageId,
                    command: commandType,
                    response: responseType,
                    detail: new TextDecoder().decode(params)
                });
            }

            this._partialMessage = Buffer.from(this._partialMessage.subarray(48 + paramsLength));
        }
    }

    private async sendMessageAndWaitForResponse(command: DebuggerCommandType, params: string | object): Promise<DebuggerResponseIPC> {
        const messageId = await this.sendMessage(command, params);
        return await this.receiveMessage(messageId);
    }

    private async sendMessage(command: DebuggerCommandType, params: string | object): Promise<UUID> {
        if (!this._debuggingProcess) {
            throw "Cannot send a message until debugger is active.";
        }

        const messageId = randomUUID();
        const message: DebuggerRequestIPC = {
            messageId,
            command,
            params: JSON.stringify(params)
        };

        console.log(`Send message: ${JSON.stringify(message)}`);

        await this.sendMessageBytes(message);

        return messageId;
    }

    private async receiveMessage(messageId: UUID): Promise<DebuggerResponseIPC> {
        if (!this._debuggingProcess) {
            throw "Cannot receive a message until debugger is active.";
        }

        const message = await this.receiveMessageBytes(messageId);

        console.log(`Receive message: ${JSON.stringify(message)}`);

        return message;
    }

    private async sendMessageBytes(message: DebuggerRequestIPC) {
        if (!this._debuggingProcess || !this._debuggingProcess.stdin) {
            throw "Cannot send a message until debugger is active.";
        }

        const messageBuffer = Buffer.from(message.messageId, 'utf-8');
        const dataView = new DataView(new ArrayBuffer(4), 0);

        dataView.setInt32(0, message.command, true);
        const commandBuffer = new Uint8Array(dataView.buffer).slice();

        const paramsBuffer = Buffer.from(message.params, 'utf-8');

        dataView.setInt32(0, paramsBuffer.length, true);
        const paramsLen = new Uint8Array(dataView.buffer).slice();

        const totalBuffer = new Uint8Array(await new Blob([messageBuffer, commandBuffer, paramsLen, paramsBuffer]).arrayBuffer());

        console.log(`Writing message buffer with len ${totalBuffer.length}, content ${totalBuffer}`);

        this._debuggingProcess.stdin.write(totalBuffer, err => {
            if (err) {
                console.log(`Failed to send message with ID ${message.messageId}, command ${message.command}`);
            }
        });
    }

    private async receiveMessageBytes(messageId: string): Promise<DebuggerResponseIPC> {
        if (!this._debuggingProcess || !this._debuggingProcess.stdout) {
            throw "Cannot receive a message until debugger is active.";
        }

        while (true) {
            // check if the requested message exists in the message list
            let foundMessage = null;
            for (let index = 0; index < this._incomingMessages.length; index++) {
                if (this._incomingMessages[index].messageId == messageId) {
                    foundMessage = index;
                    break;
                }
            }

            if (foundMessage != null) {
                const result = this._incomingMessages[foundMessage];
                this._incomingMessages.splice(foundMessage, foundMessage);
                return result;
            }

            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
}