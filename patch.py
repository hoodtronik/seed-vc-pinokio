"""
Post-install/update patch script for Seed-VC Pinokio launcher.
Fixes compatibility issues with the upstream code on Windows.
"""
import re
import os

def patch_file(filepath, patches):
    """Apply string replacements to a file."""
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filepath} not found")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    changed = False
    for old, new, desc in patches:
        if old in content:
            content = content.replace(old, new)
            print(f"  [OK] {desc}")
            changed = True
        else:
            print(f"  [SKIP] {desc} (already applied or not found)")
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def patch_file_regex(filepath, patterns):
    """Apply regex replacements to a file."""
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filepath} not found")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    changed = False
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            print(f"  [OK] {desc}")
            changed = True
        else:
            print(f"  [SKIP] {desc} (already applied or not found)")
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
    
    # 1. Fix requirements.txt: remove --pre lines
    print("Patching requirements.txt...")
    req_path = os.path.join(app_dir, 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = [l for l in f if '--pre' not in l]
        with open(req_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("  [OK] Removed --pre lines")
    
    # 2. Fix app.py: force float32 dtype
    print("Patching app.py...")
    patch_file(os.path.join(app_dir, 'app.py'), [
        ('dtype = torch.float16', 'dtype = torch.float32',
         'Force float32 dtype (prevents Half/Float mismatch)'),
    ])
    
    # 3. Fix app.py: disable streaming outputs (Gradio pydub/ffmpeg crash on Windows)
    app_py = os.path.join(app_dir, 'app.py')
    patch_file_regex(app_py, [
        # Replace streaming=True Audio outputs with non-streaming
        (r'gr\.Audio\(label="Stream Output Audio.*?streaming=True.*?\),\s*\n\s*gr\.Audio\(label="Full Output Audio.*?streaming=False.*?\)',
         'gr.Audio(label="Output Audio / 输出音频", format=\'wav\')',
         'Disable streaming audio output (fixes pydub/ffmpeg crash)'),
    ])
    
    # Replace yield-from wrappers with collecting wrappers
    patch_file(app_py, [
        # V1 wrapper
        ('    # Use yield from to properly handle the generator\n    yield from vc_wrapper_v1.convert_voice(',
         '    result = None\n    for _chunk, full_audio in vc_wrapper_v1.convert_voice(',
         'V1 wrapper: replace yield-from with collector'),
        ('        stream_output=stream_output\n    )',
         '        stream_output=True\n    ):\n        if full_audio is not None:\n            result = full_audio\n    return result',
         'V1 wrapper: return final result'),
        # V2 wrapper  
        ('    # Use yield from to properly handle the generator\n    yield from vc_wrapper_v2.convert_voice_with_streaming(',
         '    result = None\n    for _chunk, full_audio in vc_wrapper_v2.convert_voice_with_streaming(',
         'V2 wrapper: replace yield-from with collector'),
        ('        stream_output=stream_output\n    )\n',
         '        stream_output=True\n    ):\n        if full_audio is not None:\n            result = full_audio\n    return result\n',
         'V2 wrapper: return final result'),
        # Remove stream_output from function signatures
        (', stream_output=True):\n    """\n    Wrapper function for vc_wrapper.convert_voice that',
         '):\n    """\n    Wrapper function for vc_wrapper.convert_voice that',
         'V1 wrapper: remove stream_output param'),
        (', stream_output=True):\n    """\n    Wrapper function for vc_wrapper.convert_voice_with_streaming that',
         '):\n    """\n    Wrapper function for vc_wrapper.convert_voice_with_streaming that',
         'V2 wrapper: remove stream_output param'),
    ])

    print("All patches applied successfully!")

if __name__ == '__main__':
    main()
