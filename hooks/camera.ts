export function iphoneCamera(deviceList: string): string | null {
  for (const line of deviceList.split('\n')) {
    const name = line.match(/\] \[\d+\] (.*iPhone.* Camera)$/)?.[1]
    if (name !== undefined && !name.includes('Desk View')) return name
  }
  return null
}

export function captureArgs(ffmpeg: string, device: string, jpg: string, png: string): string[] {
  return [
    ffmpeg, '-hide_banner', '-loglevel', 'error', '-y',
    '-f', 'avfoundation', '-pixel_format', 'nv12', '-framerate', '30', '-video_size', '1920x1080',
    '-i', device,
    '-ss', '1.5', '-frames:v', '1', jpg,
    '-ss', '1.5', '-frames:v', '1', '-vf', 'scale=640:-2', png,
  ]
}

export function frameContext(jpg: string): string {
  return `The user attached a frame from their iPhone camera, taken right before this message: ${jpg}. Read it before answering.`
}
