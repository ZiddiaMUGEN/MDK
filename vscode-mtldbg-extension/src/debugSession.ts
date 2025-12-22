import * as vscode from 'vscode';
import {
	Logger, logger,
	LoggingDebugSession,
	InitializedEvent, TerminatedEvent, StoppedEvent, BreakpointEvent, OutputEvent,
	ProgressStartEvent, ProgressUpdateEvent, ProgressEndEvent, InvalidatedEvent,
	Thread, StackFrame, Scope, Source, Handles, Breakpoint, MemoryEvent,
	ExitedEvent
} from '@vscode/debugadapter';
import { DebugProtocol } from '@vscode/debugprotocol';

import { MTLDebugManager } from './debugManager';
import { DebuggerResponseIPC, FileAccessor } from './sharedTypes';

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
    private static threadID = 1;
    private configurationComplete = false;

    private debugManager = new MTLDebugManager();

    public constructor(fileAccessor: FileAccessor) {
		super("mtldbg.txt");

        this.setDebuggerLinesStartAt1(true);
		this.setDebuggerColumnsStartAt1(true);

		this.debugManager.on('IPC_EXIT', _ => {
			// exit early due to IPC request (e.g. an exception in the debugger, or MUGEN closing)
			this.sendEvent(new TerminatedEvent(false));
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
        /*
		response.body.exceptionBreakpointFilters = [
			{
				filter: 'namedException',
				label: "Named Exception",
				description: `Break on named exceptions. Enter the exception's name as the Condition.`,
				default: false,
				supportsCondition: true,
				conditionDescription: `Enter the exception's name`
			},
			{
				filter: 'otherExceptions',
				label: "Other Exceptions",
				description: 'This is a other exception',
				default: true,
				supportsCondition: false
			}
		];
        */

		// make VS Code send exceptionInfo request
		response.body.supportsExceptionInfoRequest = false;

		// make VS Code send setVariable request
		response.body.supportsSetVariable = true;

		// make VS Code send setExpression request
		response.body.supportsSetExpression = false;

		// make VS Code send disassemble request
		response.body.supportsDisassembleRequest = false;
		response.body.supportsSteppingGranularity = true;
		response.body.supportsInstructionBreakpoints = true;

		// make VS Code able to read and write variable memory
		response.body.supportsReadMemoryRequest = true;
		response.body.supportsWriteMemoryRequest = true;

		response.body.supportSuspendDebuggee = true;
		response.body.supportTerminateDebuggee = true;
		response.body.supportsFunctionBreakpoints = true;
		response.body.supportsDelayedStackTraceLoading = false;

		this.sendResponse(response);

		// it's OK to accept breakpoints early, we will save them + expose them to mtldbg during launch.
		this.sendEvent(new InitializedEvent());
	}

    protected configurationDoneRequest(response: DebugProtocol.ConfigurationDoneResponse, args: DebugProtocol.ConfigurationDoneArguments): void {
		super.configurationDoneRequest(response, args);
        console.log('configuration done');
        this.configurationComplete = true;
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
        while (!this.configurationComplete) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }

		// make sure to 'Stop' the buffered logging if 'trace' is not set
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
		if (args.stopOnEntry) this.sendEvent(new StoppedEvent('entry', 1));

		this.sendResponse(response);
	}

	protected async threadsRequest(response: DebugProtocol.ThreadsResponse, request?: DebugProtocol.Request) {
		// TODO: add more than just thread 1
		response.body = {
			threads: [new Thread(1, "Main thread")]
		};
		this.sendResponse(response);
	}

	protected async stackTraceRequest(response: DebugProtocol.StackTraceResponse, args: DebugProtocol.StackTraceArguments, request?: DebugProtocol.Request) {
		// TODO: stack frame is not really meaningful but we can send the line...
		response.body = {
			stackFrames: [],
			totalFrames: 0
		};
		this.sendResponse(response);
	}
}