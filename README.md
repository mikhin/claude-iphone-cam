# Claude iPhone Cam

A Claude Code mod that lets Claude see what your iPhone camera sees. Press **📷 snap** above the prompt, check the thumbnail, type your question, send.

![Claude iPhone Cam in action](https://raw.githubusercontent.com/mikhin/claude-iphone-cam/demo/demo/pies-2.gif)

The terminal in the demo is drawn, the pies are real: photos by [Joe Dumas](https://unsplash.com/photos/89zuNmg6w0Y) and [Debby Hudson](https://unsplash.com/photos/IilbCWFsHMg) on Unsplash. The demo and its build script live in the [`demo` branch](https://github.com/mikhin/claude-iphone-cam/tree/demo/demo), so installing the plugin doesn't download them.

No AirDrop, no Telegram-to-yourself, no saving files. The iPhone is already a Mac webcam through [Continuity Camera](https://support.apple.com/en-us/102546); this mod grabs one frame from it.

## Install

Inside Claude Code, run:

```
/plugin marketplace add mikhin/claude-iphone-cam
/plugin install iphone-cam
/reload-plugins
```

## Requirements

- macOS Ventura or later, iOS 16 or later, iPhone XR or newer
- Both devices on the same Apple ID, Wi-Fi and Bluetooth on, iPhone locked and near the Mac
- `ffmpeg` (`brew install ffmpeg`)
- Camera access for your terminal app (macOS asks on the first snap)

## What you see

```
[ 📷 snap ]
❯ _
```

After a snap:

```
╭──────────────╮ goes with the next message
│   (frame)    │ [ retake ]
│              │ [ drop ]
╰──────────────╯
❯ is my pie done?
```

- **retake** snaps again, **drop** forgets the frame.
- On send the frame goes with your message and the band clears.

## How it works

1. `ffmpeg -f avfoundation -list_devices` finds the device named `… iPhone … Camera` (Desk View is skipped).
2. One `ffmpeg` run waits 1.5 s for exposure, then writes a full JPEG and a 640 px PNG thumbnail to `$TMPDIR/claude-cam/`.
3. The band above the prompt draws the thumbnail with Claude Code's `Image` element.
4. On send, a `prompt.submit` hook adds the JPEG's path to the message context, and Claude reads it.

A mod can only add text to a message, not image bytes, so Claude opens the frame with one `Read` call.

## What it runs and sends

The mod runs only when you press **snap**, **retake** or **drop**, and when you send a message.

- **Programs it starts**, all on your Mac:
  - `ffmpeg -hide_banner -f avfoundation -list_devices true -i ""` lists the cameras, to find the iPhone by name
  - `ffmpeg … -i "<iPhone camera>" -ss 1.5 -frames:v 1 <frame>.jpg -ss 1.5 -frames:v 1 -vf scale=640:-2 <frame>.png` takes one frame (the full command is `captureArgs` in [`hooks/camera.ts`](hooks/camera.ts))
  - `mkdir -p $TMPDIR/claude-cam` makes the folder the frames go to
- **Files it reads and writes:** it reads the `TMPDIR` environment variable, checks that `/opt/homebrew/bin/ffmpeg` exists, and writes `frame-<n>.jpg` and `frame-<n>.png` to `$TMPDIR/claude-cam/`. It never deletes them; macOS clears that folder.
- **What it adds to your messages:** on `prompt.submit`, only for a message you typed, and only while a frame is waiting, it adds one line of context: the path of the JPEG and a request to read it. Nothing else in the message changes.
- **What it sends over the network:** nothing. The mod opens no connections. The frame reaches Anthropic only when Claude reads it, as part of the conversation, like any file Claude reads.

## License

MIT
