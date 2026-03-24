module.exports = {
  run: [{
    method: "shell.run",
    params: {
      message: "git pull --rebase --autostash"
    }
  }, {
    method: "shell.run",
    params: {
      path: "app",
      message: "git pull --rebase --autostash"
    }
  }, {
    method: "shell.run",
    params: {
      venv: "env",
      path: "app",
      message: [
        "python -c \"lines = [l for l in open('requirements.txt') if '--pre' not in l]; open('requirements.txt', 'w').writelines(lines)\"",
        "python -c \"t=open('app.py').read(); t=t.replace('dtype = torch.float16', 'dtype = torch.float32'); open('app.py','w').write(t)\"",
        "uv pip install -r requirements.txt"
      ]
    }
  }]
}
