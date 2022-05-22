const express = require("express");
const path = require("path");

const app = express();

app.use("/face", express.static("face"));

app.get("/*", (req, res) => (
  res.sendFile(path.resolve("face", "index.html"))
));

app.listen(process.env.PORT || 3001, () => console.log("Game server running"));