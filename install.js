module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    {
      method: "shell.run",
      params: {
        message: [
          "git clone https://github.com/Plachtaa/seed-vc app",
        ]
      }
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "python -c \"lines = [l for l in open('requirements.txt', encoding='utf-8') if '--pre' not in l]; open('requirements.txt', 'w', encoding='utf-8').writelines(lines)\"",
          "python -c \"t=open('app.py', encoding='utf-8').read(); t=t.replace('dtype = torch.float16', 'dtype = torch.float32'); open('app.py','w', encoding='utf-8').write(t)\"",
          "uv pip install -r requirements.txt --index-strategy unsafe-best-match",
          "uv pip install hf-xet pip"
        ]
      }
    },
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app",
          xformers: true
        }
      }
    },
    {
      method: 'input',
      params: {
        title: 'Installation completed',
        description: 'Click "Start" to get started'
      }
    }
  ]
}
