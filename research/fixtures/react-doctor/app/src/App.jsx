import { useState } from "react";
export default function App({ items }) {
  const [n, setN] = useState(0);
  return (
    <ul>
      {items.map((i, idx) => <li key={idx} onClick={() => setN(n + 1)}>{i}</li>)}
    </ul>
  );
}
