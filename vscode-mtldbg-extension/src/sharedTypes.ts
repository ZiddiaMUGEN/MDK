import { UUID } from 'crypto';

export interface FileAccessor {
	isWindows: boolean;
	readFile(path: string): Promise<Uint8Array>;
	writeFile(path: string, contents: Uint8Array): Promise<void>;
}

export enum DebuggerCommandType {
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

	IPC_EXIT = 101,
}

export enum DebuggerResponseType {
	SUCCESS = 0,
	ERROR = 1,
	EXCEPTION = 2,
}

export interface DebuggerRequestIPC {
	messageId: UUID
	command: DebuggerCommandType
	params: string | object
}

export interface DebuggerResponseIPC {
	messageId: string
	command: DebuggerCommandType
	response: DebuggerResponseType
	detail: any
}