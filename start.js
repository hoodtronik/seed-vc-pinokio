module.exports = async (kernel) => {
  let port = await kernel.port()
  return {
    requires: {
      bundle: "ai",
    },
    daemon: true,
    run: [
      {
        method: "shell.run",
        params: {
          venv: "env",
          env: {
            SERVER_NAME: "127.0.0.1",
            SERVER_PORT: port,
            GRADIO_SERVER_PORT: port
          },
          path: "app",
          message: [
            "python app.py --enable-v1 --enable-v2"
          ],
          on: [{
            "event": "/http:\/\/[0-9.:]+/",   
            "done": true
          }]
        }
      },
      {
        method: "local.set",
        params: {
          url: "{{input.event[0]}}"
        }
      }
    ]
  }
}
