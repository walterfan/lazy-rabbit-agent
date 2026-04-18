#!/usr/bin/env python3
"""
edge_tts_md_reader.py - Read a Markdown file aloud using edge-tts

Usage:
    python edge_tts_md_reader.py <markdown_file> [--voice VOICE] [--output OUTPUT] [--play] [--rate RATE]

Examples:
    # Generate MP3 from markdown
    python edge_tts_md_reader.py agent_loop_demo.md

    # Use a specific voice and play immediately
    python edge_tts_md_reader.py agent_loop_demo.md --voice en-US-AriaNeural --play

    # Chinese voice
    python edge_tts_md_reader.py agent_loop_demo.md --voice zh-CN-XiaoxiaoNeural --play

    # Adjust speed
    python edge_tts_md_reader.py agent_loop_demo.md --rate "+20%" --play

    # List available voices
    python edge_tts_md_reader.py --list-voices

Prerequisites:
    pip install edge-tts

Optional (for --play):
    macOS: afplay (built-in)
    Linux: mpv / ffplay / aplay
    Windows: start (built-in)
"""

import argparse
import asyncio
import os
import re
import subprocess
import sys
import tempfile

try:
    import edge_tts
except ImportError:
    print("Error: edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)


# ─── Markdown Cleaning ───────────────────────────────────────────────

def clean_markdown(text: str) -> str:
    """Strip markdown syntax to produce clean readable text for TTS."""

    # Remove code blocks (``` ... ```)
    text = re.sub(r'```[\s\S]*?```', ' [code block omitted] ', text)

    # Remove inline code (`...`)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)

    # Convert links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove heading markers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)

    # Remove strikethrough
    text = re.sub(r'~~([^~]+)~~', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Remove blockquote markers
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # Clean up list markers (- * + 1.)
    text = re.sub(r'^[\s]*[-*+]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove table formatting
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'^[-:]+\s*$', '', text, flags=re.MULTILINE)

    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


# ─── TTS Generation ──────────────────────────────────────────────────

async def text_to_speech(
    text: str,
    output_file: str,
    voice: str = "en-US-AriaNeural",
    rate: str = "+0%",
    volume: str = "+0%",
) -> str:
    """Convert text to speech using edge-tts and save to file."""

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
    )
    await communicate.save(output_file)
    return output_file


async def list_voices(language: str = None):
    """List available edge-tts voices, optionally filtered by language."""
    voices = await edge_tts.list_voices()

    if language:
        voices = [v for v in voices if v["Locale"].startswith(language)]

    print(f"{'Voice Name':<40} {'Language':<10} {'Gender':<8}")
    print("-" * 60)
    for v in sorted(voices, key=lambda x: x["Locale"]):
        print(f"{v['ShortName']:<40} {v['Locale']:<10} {v['Gender']:<8}")

    print(f"\nTotal: {len(voices)} voices")


# ─── Playback ─────────────────────────────────────────────────────────

def play_audio(file_path: str):
    """Play audio file using system player."""
    system = sys.platform

    try:
        if system == "darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
        elif system == "win32":  # Windows
            os.startfile(file_path)
        else:  # Linux
            for player in ["mpv", "ffplay", "aplay", "paplay"]:
                if subprocess.run(["which", player], capture_output=True).returncode == 0:
                    cmd = [player]
                    if player == "ffplay":
                        cmd += ["-nodisp", "-autoexit"]
                    cmd.append(file_path)
                    subprocess.run(cmd, check=True)
                    return
            print(f"No audio player found. File saved at: {file_path}")
    except Exception as e:
        print(f"Playback error: {e}")
        print(f"File saved at: {file_path}")


# ─── Chunking for long texts ─────────────────────────────────────────

def chunk_text(text: str, max_chars: int = 5000) -> list[str]:
    """Split text into chunks at paragraph boundaries to stay within TTS limits."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


# ─── Main ─────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="Read a Markdown file aloud using edge-tts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Popular voices:
  English:  en-US-AriaNeural, en-US-GuyNeural, en-GB-SoniaNeural
  Chinese:  zh-CN-XiaoxiaoNeural, zh-CN-YunxiNeural, zh-CN-XiaoyiNeural
  Japanese: ja-JP-NanamiNeural
  Korean:   ko-KR-SunHiNeural
  French:   fr-FR-DeniseNeural
  German:   de-DE-KatjaNeural
        """,
    )
    parser.add_argument("markdown_file", nargs="?", help="Path to the markdown file")
    parser.add_argument("--voice", "-v", default="en-US-AriaNeural",
                        help="TTS voice name (default: en-US-AriaNeural)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output MP3 file path (default: <input_name>.mp3)")
    parser.add_argument("--play", "-p", action="store_true",
                        help="Play audio after generation")
    parser.add_argument("--rate", "-r", default="+0%",
                        help="Speech rate, e.g. '+20%%' or '-10%%' (default: +0%%)")
    parser.add_argument("--volume", default="+0%",
                        help="Volume adjustment (default: +0%%)")
    parser.add_argument("--list-voices", "-l", action="store_true",
                        help="List available voices and exit")
    parser.add_argument("--language", default=None,
                        help="Filter voices by language code (e.g. 'en', 'zh', 'ja')")
    parser.add_argument("--max-chars", type=int, default=50000,
                        help="Max characters to read (default: 50000)")

    args = parser.parse_args()

    # List voices mode
    if args.list_voices:
        await list_voices(args.language)
        return

    if not args.markdown_file:
        parser.print_help()
        sys.exit(1)

    # Read markdown file
    md_path = args.markdown_file
    if not os.path.exists(md_path):
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    print(f"📖 Reading: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Clean markdown
    clean_text = clean_markdown(raw_text)

    # Truncate if too long
    if len(clean_text) > args.max_chars:
        clean_text = clean_text[:args.max_chars]
        print(f"⚠️  Text truncated to {args.max_chars} characters")

    print(f"📝 Cleaned text: {len(clean_text)} characters")

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(os.path.basename(md_path))[0]
        output_dir = os.path.dirname(md_path) or "."
        output_path = os.path.join(output_dir, f"{base_name}.mp3")

    # Split into chunks for long texts
    chunks = chunk_text(clean_text)
    print(f"🔊 Voice: {args.voice} | Rate: {args.rate} | Chunks: {len(chunks)}")

    if len(chunks) == 1:
        # Single chunk - direct generation
        print(f"🎙️  Generating speech...")
        await text_to_speech(clean_text, output_path, args.voice, args.rate, args.volume)
    else:
        # Multiple chunks - generate and concatenate
        temp_files = []
        try:
            for i, chunk in enumerate(chunks):
                print(f"🎙️  Generating chunk {i+1}/{len(chunks)}...")
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_files.append(temp_file.name)
                temp_file.close()
                await text_to_speech(chunk, temp_file.name, args.voice, args.rate, args.volume)

            # Concatenate with ffmpeg if available, otherwise use first chunk
            if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0:
                list_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
                for tf in temp_files:
                    list_file.write(f"file '{tf}'\n")
                list_file.close()

                subprocess.run([
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", list_file.name, "-c", "copy", output_path
                ], capture_output=True, check=True)
                os.unlink(list_file.name)
            else:
                # Fallback: simple binary concatenation (works for MP3)
                with open(output_path, "wb") as outf:
                    for tf in temp_files:
                        with open(tf, "rb") as inf:
                            outf.write(inf.read())
        finally:
            for tf in temp_files:
                if os.path.exists(tf):
                    os.unlink(tf)

    file_size = os.path.getsize(output_path)
    print(f"✅ Saved: {output_path} ({file_size / 1024:.1f} KB)")

    # Play if requested
    if args.play:
        print("▶️  Playing...")
        play_audio(output_path)


if __name__ == "__main__":
    asyncio.run(main())
