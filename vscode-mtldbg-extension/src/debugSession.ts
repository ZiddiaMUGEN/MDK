import * as vscode from 'vscode';
import {
	Logger, logger,
	LoggingDebugSession,
	InitializedEvent, TerminatedEvent, StoppedEvent, BreakpointEvent, OutputEvent,
	ProgressStartEvent, ProgressUpdateEvent, ProgressEndEvent, InvalidatedEvent,
	Thread, StackFrame, Scope, Source, Handles, Breakpoint, MemoryEvent,
	ExitedEvent,
	Variable
} from '@vscode/debugadapter';
import { DebugProtocol } from '@vscode/debugprotocol';

import { MTLDebugManager } from './debugManager';
import { VariableType, FileAccessor } from './sharedTypes';

interface ILaunchRequestArguments extends DebugProtocol.LaunchRequestArguments {
	/** An absolute path to the program to debug. */
	program: string;
    /** An absolute path to the database containing debugging information. */
	database: string;
    /** An absolute path to the Python executable to use for compilation. */
	pythonPath: string;
    /** An absolute path to the MUGEN executable to use for debugging. */
	mugenPath: string;
	/** Automatically stop target after launch. If not specified, target does not stop. */
	stopOnEntry?: boolean;
	/** Build the character before launching the debugger. */
	build?: boolean;
}

export class MTLDebugSession extends LoggingDebugSession {
    private initializationComplete = false;

    private debugManager = new MTLDebugManager();

    public constructor(fileAccessor: FileAccessor) {
		super("mtldbg.txt");

        this.setDebuggerLinesStartAt1(true);
		this.setDebuggerColumnsStartAt1(true);

		this.debugManager.on('IPC_EXIT', evt => {
			// exit early due to IPC request (e.g. an exception in the debugger, or MUGEN closing)
			if (evt.detail === "DEBUGGER_INVALID_DEBUG_DATABASE") {
				vscode.window.showErrorMessage("Debugger has been closed due to an incompatible debugging database.");
			}
			console.log(evt.detail);
			this.sendEvent(new TerminatedEvent(false));
		});

		this.debugManager.on('IPC_HIT_BREAKPOINT', evt => {
			// pause due to breakpoint
			this.sendEvent(new StoppedEvent('breakpoint', JSON.parse(evt.detail).owner));
		});

		this.debugManager.on('IPC_STEP', evt => {
			// pause due to breakpoint
			this.sendEvent(new StoppedEvent('step', JSON.parse(evt.detail).owner));
		});
    }

    protected initializeRequest(response: DebugProtocol.InitializeResponse, args: DebugProtocol.InitializeRequestArguments): void {
		// build and return the capabilities of this debug adapter:
		response.body = response.body || {};

		// the adapter implements the configurationDone request.
		response.body.supportsConfigurationDoneRequest = true;

		// make VS Code use 'evaluate' when hovering over source
		response.body.supportsEvaluateForHovers = true;

		// make VS Code show a 'step back' button
		response.body.supportsStepBack = false;

		// make VS Code support data breakpoints
		response.body.supportsDataBreakpoints = false;

		// make VS Code support completion in REPL
		response.body.supportsCompletionsRequest = false;
		//response.body.completionTriggerCharacters = [ ".", "[" ];

		// make VS Code send cancel request
		response.body.supportsCancelRequest = true;

		// make VS Code send the breakpointLocations request
		response.body.supportsBreakpointLocationsRequest = true;

		// make VS Code provide "Step in Target" functionality
		response.body.supportsStepInTargetsRequest = true;

		// the adapter defines two exceptions filters, one with support for conditions.
		response.body.supportsExceptionFilterOptions = false;

		// make VS Code send exceptionInfo request
		response.body.supportsExceptionInfoRequest = false;

		// make VS Code send setVariable request
		response.body.supportsSetVariable = true;

		// make VS Code send setExpression request
		response.body.supportsSetExpression = false;

		// make VS Code send disassemble request
		response.body.supportsDisassembleRequest = false;
		response.body.supportsSteppingGranularity = true;
		response.body.supportsInstructionBreakpoints = false;
		response.body.supportsDataBreakpoints = false;
		response.body.supportsFunctionBreakpoints = false;

		// make VS Code able to read and write variable memory
		response.body.supportsReadMemoryRequest = true;
		response.body.supportsWriteMemoryRequest = true;

		response.body.supportSuspendDebuggee = true;
		response.body.supportTerminateDebuggee = true;
		response.body.supportsFunctionBreakpoints = true;
		response.body.supportsDelayedStackTraceLoading = false;
		response.body.supportsSingleThreadExecutionRequests = true;

		response.body.breakpointModes = [
			{ mode: "pp", label: "Passpoint", description: "Breaks at a controller only if the triggers evaluate to true.", appliesTo: ['source'] },
			{ mode: "bp", label: "Breakpoint", description: "Breaks every time a controller is evaluated, even if the triggers evaluate to false.", appliesTo: ['source'] }
		];

		this.initializationComplete = true;
		this.sendResponse(response);
	}

    protected configurationDoneRequest(response: DebugProtocol.ConfigurationDoneResponse, args: DebugProtocol.ConfigurationDoneArguments): void {
		super.configurationDoneRequest(response, args);
        console.log('configuration done');
	}

    protected async disconnectRequest(response: DebugProtocol.DisconnectResponse, args: DebugProtocol.DisconnectArguments, request?: DebugProtocol.Request) {
		console.log(`disconnectRequest suspend: ${args.suspendDebuggee}, terminate: ${args.terminateDebuggee}`);
        if (this.debugManager.isConnected()) {
            await this.debugManager.disconnect();
        }
	}

    protected async attachRequest(response: DebugProtocol.AttachResponse, args: ILaunchRequestArguments) {
		throw "Can't attach to an existing MUGEN session.";
	}

    protected async launchRequest(response: DebugProtocol.LaunchResponse, args: ILaunchRequestArguments) {
        // wait for configuration.
        while (!this.initializationComplete) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }

		logger.setup(Logger.LogLevel.Verbose, false);

		// start the program in the runtime
		if (args.build) {
			console.log(`Launch build for program ${args.program}.`)
			
			if (args.program.endsWith(".py")) {
				// build with MDK
				const terminal = vscode.window.createTerminal({ name: `MDK Build ${args.program}`, hideFromUser: true });
				terminal.show();
				terminal.sendText(`${args.pythonPath} "${args.program}"`, false);
				terminal.sendText("; exit");
				const result = await new Promise((resolve, reject) => {
					const disposeToken = vscode.window.onDidCloseTerminal(
						async (closedTerminal) => {
							if (closedTerminal === terminal) {
								disposeToken.dispose();
								if (terminal.exitStatus !== undefined) {
									resolve(terminal.exitStatus);
								} else {
									reject("Terminal exited with undefined status");
								}
							}
						}
					);
				});
			} else {
				// build with MTL
				throw "Build with MTL not currently implemented, try MDK.";
			}
		}

        // launch debugger
        await this.debugManager.connect(args.pythonPath, args.database, args.mugenPath, args.stopOnEntry);

		// manager is connected, so allow breakpoint initialization
		this.sendEvent(new InitializedEvent());

		// trigger a stop so that the debugger knows it is paused
		if (args.stopOnEntry) this.sendEvent(new StoppedEvent('entry', 1));

		this.sendResponse(response);
	}

	protected async continueRequest(response: DebugProtocol.ContinueResponse, args: DebugProtocol.ContinueArguments, request?: DebugProtocol.Request) {
		// just send a CONTINUE to the debugger, threads aren't real
		if (args.singleThread && args.threadId !== 1) {
			// note: this currently won't ever be hit as vscode doesn't support the `singleThread` parameter.
			// support for this is included anyway so we can benefit if they ever allow it.
			await this.debugManager.setStepTarget(args.threadId);
		}
		await this.debugManager.continue();
		response.body = { allThreadsContinued: (!args.singleThread || args.threadId === 1) };
		this.sendResponse(response);
	}

	protected async pauseRequest(response: DebugProtocol.PauseResponse, args: DebugProtocol.PauseArguments, request?: DebugProtocol.Request) {
		// send a BREAK to the debugger, threads aren't real
		await this.debugManager.pause();
		this.sendResponse(response);
		
		if (args.threadId === 1) {
			// we need to send a pause event for ALL player IDs (thread IDs)
			const playerList = await this.debugManager.requestPlayerList();
			for (const player of playerList) {
				this.sendEvent(new StoppedEvent('pause', player.id));
			}
		} else {
			// just pause the target 'thread' (player)
			this.sendEvent(new StoppedEvent('pause', args.threadId));
		}
		
	}

	protected async threadsRequest(response: DebugProtocol.ThreadsResponse, request?: DebugProtocol.Request) {
		// threads here will be 'symbolic threads' which track the state of the player and its helpers.
		// thread ID will be the player ID, thread name will be the player name.
		const playerList = await this.debugManager.requestPlayerList();

		const threads = playerList.map(x => new Thread(x.id, x.name));
		if (threads.length === 0) threads.push(new Thread(1, "Launch"));

		response.body = {
			threads
		};
		this.sendResponse(response);
	}

	protected async stackTraceRequest(response: DebugProtocol.StackTraceResponse, args: DebugProtocol.StackTraceArguments, request?: DebugProtocol.Request) {
		// TODO: stack frame is not really meaningful but we can send the line...
		if (args.threadId === 1) {
			// launch thread, just return empty
			response.body = {
				stackFrames: [],
				totalFrames: 0
			};
		} else {
			// get the current frame for this player.
			const playerDetails = await this.debugManager.requestPlayerDetails(args.threadId);
			// if the player's data fetch failed (e.g. because they are p2) respond with empty stackframes.
			if (playerDetails.id === 0) {
				response.body = {
					stackFrames: [],
					totalFrames: 0
				};
				this.sendResponse(response);
				return;
			}

			const fileName = await this.findLocalFileName(playerDetails.frame.fileName);
			const frame = new StackFrame(playerDetails.id, playerDetails.frame.stateNameOrId, new Source(playerDetails.frame.stateNameOrId, fileName, undefined, undefined, undefined), playerDetails.frame.lineNumber, 1);
			response.body = {
				stackFrames: [frame],
				totalFrames: 1
			};
		}
		this.sendResponse(response);
	}

	protected async scopesRequest(response: DebugProtocol.ScopesResponse, args: DebugProtocol.ScopesArguments, request?: DebugProtocol.Request) {
		const teamside = await this.debugManager.getPlayerTeamside(args.frameId);
		const baseReference = args.frameId << 8;

		if (teamside === 1) {
			response.body = {
				scopes: [
					new Scope("Globals", baseReference + VariableType.GLOBAL, false),
					new Scope("Locals", baseReference + VariableType.LOCAL, false),
					new Scope("Autos", baseReference + VariableType.AUTO, false),
					new Scope("Indexed Var", baseReference + VariableType.INDEXED_INT, false),
					new Scope("Indexed Fvar", baseReference + VariableType.INDEXED_FLOAT, false),
					new Scope("Indexed Sysvar", baseReference + VariableType.INDEXED_SYSINT, false),
					new Scope("Indexed Sysfvar", baseReference + VariableType.INDEXED_SYSFLOAT, false)
				]
			};
		} else {
			response.body = {
				scopes: [
					new Scope("Indexed Var", baseReference + VariableType.INDEXED_INT, false),
					new Scope("Indexed Fvar", baseReference + VariableType.INDEXED_FLOAT, false),
					new Scope("Indexed Sysvar", baseReference + VariableType.INDEXED_SYSINT, false),
					new Scope("Indexed Sysfvar", baseReference + VariableType.INDEXED_SYSFLOAT, false)
				]
			};
		}
		

		this.sendResponse(response);
	}

	protected async variablesRequest(response: DebugProtocol.VariablesResponse, args: DebugProtocol.VariablesArguments, request?: DebugProtocol.Request) {
		const playerID = args.variablesReference >> 8;
		const variableType = args.variablesReference - (playerID << 8);
		
		const playerVariables = await this.debugManager.getPlayerVariables(playerID, variableType);

		response.body = { variables: playerVariables.map(x => new Variable(x.name, x.value.toString())) };

		this.sendResponse(response);
	}

	protected async evaluateRequest(response: DebugProtocol.EvaluateResponse, args: DebugProtocol.EvaluateArguments, request?: DebugProtocol.Request) {
		const playerVariables = await this.debugManager.getPlayerVariables(args.frameId ?? 0, VariableType.ALL);
		const match = playerVariables.find(x => x.name.toLowerCase() === args.expression.toLowerCase());
		if (match) {
			response.body = {
				result: `${args.expression}: ${match.value.toString()}`,
				variablesReference: 0
			};
		}
		this.sendResponse(response);
	}

	protected async setBreakPointsRequest(response: DebugProtocol.SetBreakpointsResponse, args: DebugProtocol.SetBreakpointsArguments, request?: DebugProtocol.Request) {
		response.body = {
			breakpoints: []
		};

		if (this.debugManager.isConnected()) {
			if (args.source.path && args.breakpoints) {
				// clear breakpoints for this file
				await this.debugManager.clearFileBreakpoints(args.source.path);
				// set breakpoints
				for (var bp of args.breakpoints) {
					const set = await this.debugManager.setBreakpoint(args.source.path, bp.line, bp.mode ?? "pp");
					if (!set.filename) {
						response.body.breakpoints.push({
							verified: false,
							reason: 'failed',
							message: set
						});
					} else {
						// adapter-internal ID is 100+ for breakpoints, just to differentiate
						const fileName = await this.findLocalFileName(set.filename);
						response.body.breakpoints.push({
							id: set.id + (bp.mode === "bp" ? 100 : 0),
							verified: true,
							source: new Source(fileName, fileName, undefined, undefined, undefined),
							line: set.line,
							column: 1
						});
					}
				}
			}
		}

		this.sendResponse(response);
	}

	protected async nextRequest(response: DebugProtocol.NextResponse, args: DebugProtocol.NextArguments, request?: DebugProtocol.Request) {
		if (this.debugManager.isConnected() && args.threadId !== 1) {
			await this.debugManager.setStepTarget(args.threadId);
			await this.debugManager.step(args.threadId);
		}
		this.sendResponse(response);
	}

	protected async stepInRequest(response: DebugProtocol.StepInResponse, args: DebugProtocol.StepInArguments, request?: DebugProtocol.Request) {
		if (this.debugManager.isConnected() && args.threadId !== 1) {
			await this.debugManager.setStepTarget(args.threadId);
			await this.debugManager.step(args.threadId);
		}
		this.sendResponse(response);
	}

	private async findLocalFileName(fileName: string) {
		const matches = await vscode.workspace.findFiles(`${fileName.replaceAll('\\', '/')}`);
		if (matches.length === 1) {
			fileName = matches[0].fsPath;
		} else if (matches.length > 1) {
			fileName = matches.reduce((a, b) => a.fsPath.length <= b.fsPath.length ? a : b).fsPath;
		}

		return fileName;
	}
}