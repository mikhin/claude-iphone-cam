export type Frame = { jpg: string; png: string; generation: number }

export type Shot = { kind: 'idle' } | { kind: 'busy' } | { kind: 'ready'; frame: Frame } | { kind: 'failed'; reason: string }

declare module 'claude-code' {
  interface PluginState {
    'iphone-cam': { shot: Shot }
  }
}
