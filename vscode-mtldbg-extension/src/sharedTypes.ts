import { UUID } from 'crypto';

export interface FileAccessor {
	isWindows: boolean;
	readFile(path: string): Promise<Uint8Array>;
	writeFile(path: string, contents: Uint8Array): Promise<void>;
}

export enum VariableType {
	GLOBAL = 0,
	LOCAL = 1,
	AUTO = 2,
	INDEXED_INT = 3,
	INDEXED_FLOAT = 4,
	INDEXED_SYSINT = 5,
	INDEXED_SYSFLOAT = 6,
	ALL = 99
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

	// commands used specifically by IPC
	// 1xx commands are mtldbg -> adapater
	// 2xx commands are adapter -> mtldbg
	IPC_EXIT = 101,
	IPC_HIT_BREAKPOINT = 102,
	IPC_STEP = 103,
	IPC_GENERATE = 104,

	IPC_LIST_PLAYERS = 201,
	IPC_GET_PLAYER_INFO = 202,
	IPC_PAUSE = 203,
	IPC_GET_VARIABLES = 204,
	IPC_GET_TEAMSIDE = 205,
	IPC_CLEAR_BREAKPOINTS = 206,
	IPC_SET_BREAKPOINT = 207,
	IPC_SET_STEP_TARGET = 208,
	IPC_GET_TRIGGER = 209,
}

export enum DebuggerResponseType {
	SUCCESS = 0,
	ERROR = 1,
	EXCEPTION = 2,
}

export interface DebuggerRequestIPC {
	messageId: UUID
	command: DebuggerCommandType
	params: string
}

export interface DebuggerResponseIPC {
	messageId: string
	command: DebuggerCommandType
	response: DebuggerResponseType
	detail: string
}