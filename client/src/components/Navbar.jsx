import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav style={{ padding: "10px", background: "#1f2937", color: "white" }}>
      <Link to="/" style={{ marginRight: "20px", color: "white" }}>
        Prediction
      </Link>
      <Link to="/dashboard" style={{ color: "white" }}>
        Dashboard
      </Link>
    </nav>
  );
}

export default Navbar;