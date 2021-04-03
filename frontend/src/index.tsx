import { CookiesProvider } from "react-cookie";
import ReactDOM from "react-dom";
import React from "react";

import "./index.css";
import App from "./App";

ReactDOM.render(
  <React.StrictMode>
    <CookiesProvider>
      <App />
    </CookiesProvider>
  </React.StrictMode>,
  document.getElementById("root"),
);
