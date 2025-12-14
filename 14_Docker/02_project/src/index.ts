import { createServer } from "./app/server";

const PORT = process.env.PORT ? +process.env.PORT : 3000;

const app = createServer();

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
