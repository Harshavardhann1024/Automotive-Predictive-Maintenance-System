import React from "react";

export default function ErrorState({ message = "Something went wrong" }) {
  return (
    <div className="error-state">
      <h3>Error</h3>
      <p>{message}</p>
    </div>
  );
}
