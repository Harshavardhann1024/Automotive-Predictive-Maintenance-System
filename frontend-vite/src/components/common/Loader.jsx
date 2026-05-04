import React from "react";

export default function Loader({ message = "Loading..." }) {
  return (
    <div className="loader" role="status">
      <span className="spinner" aria-hidden="true"></span>
      <span>{message}</span>
    </div>
  );
}
