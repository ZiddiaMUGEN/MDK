import { ChildProcess, spawn } from 'child_process';
import { randomUUID, UUID } from 'crypto';
import Stream from 'stream';

const MINIMUM_RESPONSE_LENGTH = 48;

enum DebuggerCommandType {
    EXIT = -1,
    NONE = 0,
    HELP = 1,
    LAUNCH = 2,
    LOAD = 3,
    CONTINUE = 4,
    INFO = 5,
    BREAK = 6,
    STEP = 7,
    STOP = 8,
    DELETE = 9,
    BREAKP = 10,
    DELETEP = 11,
}

enum DebuggerResponseType {
    SUCCESS = 0,
    ERROR = 1,
    EXCEPTION = 2,
}

interface DebuggerRequestIPC {
    messageId: UUID
    command: DebuggerCommandType
    params: string | object
}

interface DebuggerResponseIPC {
    messageId: string
    command: DebuggerCommandType
    response: DebuggerResponseType
    detail: any
}

export class MTLDebugManager {
    private _debuggingProcess: ChildProcess | null = null;
    private _incomingMessages: DebuggerResponseIPC[] = [];

    private _partialMessage: Buffer | null = null;

    public async connect(python: string, database: string, mugen: string) {
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
        await this.sendMessageAndWaitForResponse(DebuggerCommandType.LAUNCH, "");
    }

    public async disconnect() {
        // send `stop` and `exit` commands to the debugging process
        if (this._debuggingProcess && this._debuggingProcess.pid) {
            console.log("Attempting to gracefully stop debugging.");
            await this.sendMessageAndWaitForResponse(DebuggerCommandType.STOP, "");
            await this.sendMessageAndWaitForResponse(DebuggerCommandType.EXIT, "");
            this._debuggingProcess.kill();
        }

        // clean up
        this._debuggingProcess = null;
        this._incomingMessages = [];
        this._partialMessage = null;
    }

    public isConnected() {
        return this._debuggingProcess != null;
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

            this._incomingMessages.push({
                messageId: inboundMessageId,
                command: commandType,
                response: responseType,
                detail: new TextDecoder().decode(params)
            });

            console.log(`Received new message with messageId ${inboundMessageId}, command ${commandType}, response ${responseType}`);

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
            params
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

        let paramsString: string;
        try {
            paramsString = JSON.stringify(message.params);
        } catch {
            paramsString = message.params as string;
        }
        const paramsBuffer = Buffer.from(paramsString, 'utf-8');

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