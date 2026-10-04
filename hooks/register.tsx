import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Shot } from '../types'
import { captureArgs, frameContext, iphoneCamera } from './camera'

const HOMEBREW_FFMPEG = '/opt/homebrew/bin/ffmpeg'
const THUMB_COLUMNS = 24
const THUMB_ROWS = 7

const shot = atom({ plugin: 'iphone-cam', key: 'shot' } as const, { kind: 'idle' } as Shot)

let generation = 0

function setShot($: EngineInterface, next: Shot): Promise<Shot> {
  return update($, shot, () => next)
}

async function snap($: EngineInterface): Promise<void> {
  await setShot($, { kind: 'busy' })
  const ffmpeg = (await $.fs.exists(HOMEBREW_FFMPEG)) ? HOMEBREW_FFMPEG : 'ffmpeg'
  const list = await $.process.run([ffmpeg, '-hide_banner', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''])
  const device = iphoneCamera(list.stderr)
  if (device === null) {
    await setShot($, { kind: 'failed', reason: 'iPhone camera not found: lock it, keep it near, Wi-Fi and Bluetooth on' })
    return
  }
  const dir = `${(await $.env.get('TMPDIR')) ?? '/tmp/'}claude-cam`
  await $.process.run(['mkdir', '-p', dir])
  generation += 1
  const jpg = `${dir}/frame-${generation}.jpg`
  const png = `${dir}/frame-${generation}.png`
  const run = await $.process.run(captureArgs(ffmpeg, device, jpg, png), { timeoutMs: 20_000 })
  if (run.exitCode !== 0 || !(await $.fs.exists(png))) {
    await setShot($, { kind: 'failed', reason: run.stderr.trim().split('\n').pop() ?? 'ffmpeg failed' })
    return
  }
  await setShot($, { kind: 'ready', frame: { jpg, png, generation } })
}

export const register: Register = on => {
  on('prompt.submit', async ($, e, next) => {
    const current = await read($, shot)
    if (current.kind !== 'ready' || e.origin.kind !== 'composer') return next(e)
    await setShot($, { kind: 'idle' })
    return next({ ...e, context: [...(e.context ?? []), frameContext(current.frame.jpg)] })
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.surface !== 'terminal' || e.props.hasSurvey) return next(e)
    const current = await read($, shot)
    const below = await next(e)
    const { Box, Button, Image, Text } = $.ui.resolve(e)
    const press = () => snap($)
    const clear = () => setShot($, { kind: 'idle' })

    return (
      <Box flexDirection="column">
        {current.kind === 'ready' ? (
          <Box flexDirection="row" columnGap={1}>
            <Image
              key="frame"
              source={{ file: current.frame.png, format: 'png', generation: current.frame.generation }}
              columns={THUMB_COLUMNS}
              rows={THUMB_ROWS}
              alt="[camera frame]"
            />
            <Box flexDirection="column">
              <Text dimColor>goes with the next message</Text>
              <Button key="retake" label="retake" onPress={press} />
              <Button key="drop" label="drop" onPress={clear} />
            </Box>
          </Box>
        ) : (
          <Box flexDirection="row" columnGap={1}>
            {current.kind === 'busy' ? (
              <Text dimColor>snapping…</Text>
            ) : (
              <Button key="snap" label="📷 snap" onPress={press} />
            )}
            {current.kind === 'failed' ? <Text color="red" wrap="truncate">{current.reason}</Text> : null}
          </Box>
        )}
        {below}
      </Box>
    )
  })
}
