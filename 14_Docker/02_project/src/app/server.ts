import express, { Application, Request, Response } from "express";

export function createServer(): Application {
  const app = express();

  app.use(express.json());

  app.get("/", (req: Request, res: Response) => {
    res.send("Hello from TypeScript Express server!");
  });

  return app;
}
