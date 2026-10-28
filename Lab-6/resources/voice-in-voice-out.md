# Voice in, voice out

*Optional reading for the Lab 6 stretch. Lecture Chapter 3 in more depth, with the costs worked out.*

## 1. The concept, in plain language

A voice feature is two conversions wrapped around the chat you already have: **speech to text** (STT) turns the person's clip into a question; your normal chat turn answers it; **text to speech** (TTS) turns the answer into audio the browser plays. Nothing in the middle changes. If your chat turn is grounded, uses tools and remembers interests, so does the voice version, for free.

Two ways to do each conversion:

- **STT.** Send the audio to a model that accepts audio input (Gemini 3.8 Flash does, through OpenRouter, as an `input_audio` part in an ordinary chat call) and ask it to transcribe. Or use a dedicated speech model. The first keeps one client and one key; the second is often more accurate on noisy audio and supports streaming transcription.
- **TTS.** Call a text-to-speech endpoint (OpenRouter serves several TTS models at `POST /api/v1/audio/speech`, including `google/gemini-3.8-flash-lite-tts`) and get bytes back. Or use the browser's built-in `speechSynthesis`, which costs nothing and sounds like it.

CampusPulse uses the first option for both: one provider, one key, two more functions in `llm.py`.

## 2. Why it matters in production

**Latency compounds.** A voice turn is STT (a few hundred milliseconds for a short clip) plus the chat turn plus TTS (often a second or more for a paragraph). Four seconds of silence after you stop talking feels broken. Real voice products stream every stage; CampusPulse streams the text stage only and keeps the spoken answer short (two or three sentences, and `speak()` caps the input at 1,500 characters). Know what you are not building.

**Audio is personal data you must not keep.** A recording of someone's voice is identifying. The right default is to transcribe it in memory and throw it away in the same request. CampusPulse never writes the clip to disk, and a test checks that.

**Costs are different in shape.** Audio input is priced per token, and audio becomes tokens at a fixed rate: 32 tokens per second for Gemini, so a 5-second question is about 160 tokens, or roughly $0.0001 at $0.75 per million. TTS is priced per token of text in and audio out: a 60-word answer is roughly 80 input tokens, and the output tokens are what you pay most for ($6 per million for the Lite TTS model). Per turn these are tiny. Per 10,000 users a day they are a line item. The log line per call (`kind: transcribe`, `kind: speak`) is how you find out.

**A failure story.** A hackathon team built a voice assistant that recorded at the browser's default (48 kHz stereo WebM) and uploaded raw recordings. Each 10-second clip was about 150 KB, uploads were slow on campus Wi-Fi, and the provider rejected the format. They spent the demo day on encoding. Converting to 16 kHz mono WAV in the browser (which CampusPulse's page does with the Web Audio API) makes the clip a third of the size and a format every provider accepts, and speech needs nothing above 16 kHz.

## 3. Worked example on CampusPulse

**Recording and converting.** `static/index.html` records with `MediaRecorder` while the button is held, then `toWav()` decodes the blob with `AudioContext.decodeAudioData`, resamples to 16 kHz mono with an `OfflineAudioContext`, and writes a 44-byte WAV header in front of the 16-bit samples. The result is posted as multipart `clip`.

**Transcribing.** `transcribe(audio, fmt)` in `src/llm.py` sends one user message with two parts: a text instruction ("Transcribe this audio exactly. Reply with the words only.") and `{"type": "input_audio", "input_audio": {"data": <base64>, "format": "wav"}}`. Temperature 0. The usage line it logs has `kind: transcribe`; the token count tells you the clip's length at 32 tokens a second.

**Answering.** `POST /voice` in `src/app.py` calls `answer_text()`, the non-streamed convenience over the same `chat_turn()` the text path uses, with the same session and student headers. If the transcript is "remember that I like tech talks", the tool runs, with the same gates.

**Speaking.** `speak(text)` calls `client.audio.speech.create(model=TTS_MODEL, input=text, voice="Kore", response_format="pcm")`. Gemini TTS returns raw 24 kHz 16-bit mono PCM; `pcm_to_wav()` adds the header with the standard library's `wave` module so the browser's `Audio` element can play it from a data URL. The byte stream carries no usage block, so the log line is marked `estimated: true`; the exact charge is on your OpenRouter generation record.

**Offline.** `src/offline.py` has stand-ins: `transcribe()` returns the text after a `TEXT:` marker in the bytes (so a test can make a fake clip "say" anything), and `speak()` returns 0.3 seconds of silence. Real audio needs the real model.

## 4. Common mistakes and how to spot them

- **Sending the raw recording.** Large, slow, wrong format. Convert in the browser.
- **Storing the clip "for debugging".** Then forgetting it. If you must, write a lifetime in the contract and delete on it.
- **Speaking the whole answer.** A six-paragraph answer read aloud is unusable. Ask the model for two or three sentences in the voice path's system prompt, and cap the TTS input.
- **Trusting the transcript blindly.** STT mishears names and ids ("ev-201" becomes "EV to a one"). The transcript goes through the same tool contracts as typed text, so a bad id fails validation rather than booking the wrong thing. Show the transcript to the person so they can see what was heard.
- **No cost line.** Two extra model calls per voice turn with nothing in the usage log is a budget you cannot see.
- **Assuming the browser allows the microphone.** `getUserMedia` needs HTTPS or localhost and a user gesture. Hold-to-talk is the gesture.

## 5. Check yourself

1. A 12-second question in a noisy corridor is transcribed as "book be two or four tomorrow at three". What catches it before anything is booked, and what should the UI show?
2. Estimate the audio-input cost of 2,000 voice questions a day averaging 6 seconds each, at 32 tokens a second and $0.75 per million tokens.
3. Why does CampusPulse convert to WAV in the browser instead of on the server? Give one reason about size and one about format.
