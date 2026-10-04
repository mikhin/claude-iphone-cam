import { expect, test } from 'claude-code/testing'

import { captureArgs, iphoneCamera } from '../hooks/camera'

const DEVICES = [
  '[AVFoundation indev @ 0x1] AVFoundation video devices:',
  '[AVFoundation indev @ 0x1] [0] FaceTime HD Camera',
  '[AVFoundation indev @ 0x1] [1] Jane’s iPhone Desk View Camera',
  '[AVFoundation indev @ 0x1] [2] Jane’s iPhone Camera',
  '[AVFoundation indev @ 0x1] [3] Capture screen 0',
  '[AVFoundation indev @ 0x1] [3] Jane’s iPhone Microphone',
].join('\n')

test('the iPhone camera is picked over the Mac camera and Desk View', () => {
  expect(iphoneCamera(DEVICES)).toBe('Jane’s iPhone Camera')
})

test('an iPhone named after its model alone is found too', () => {
  expect(iphoneCamera('[AVFoundation indev @ 0x1] [1] iPhone Camera')).toBe('iPhone Camera')
})

test('no iPhone in the list means no camera', () => {
  expect(iphoneCamera('[AVFoundation indev @ 0x1] [0] FaceTime HD Camera')).toBeNull()
})

test('one capture writes the full jpg and a scaled png thumbnail', () => {
  const args = captureArgs('ffmpeg', 'iPhone Camera', '/t/f.jpg', '/t/f.png')
  expect(args[args.indexOf('-i') + 1]).toBe('iPhone Camera')
  expect(args.indexOf('/t/f.jpg')).toBeLessThan(args.indexOf('scale=640:-2'))
  expect(args.at(-1)).toBe('/t/f.png')
})
