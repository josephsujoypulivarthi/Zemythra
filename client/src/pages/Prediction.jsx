import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { predictRisk } from "../services/api";

function Prediction() {
  const [formData, setFormData] = useState({
    age: "",
    glucose: "",
    bmi: "",
  });

  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: Number(e.target.value),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await predictRisk(formData);
      setResult(res.data);
    } catch (error) {
      console.error(error.response || error);
      alert("Backend connection error");
    }
  };

  const goToDashboard = () => {
    navigate("/dashboard", { state: { result } });
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Risk Prediction</h2>

      <form onSubmit={handleSubmit}>
        <input type="number" name="age" placeholder="Age" onChange={handleChange} />
        <br /><br />

        <input type="number" name="glucose" placeholder="Glucose" onChange={handleChange} />
        <br /><br />

        <input type="number" name="bmi" placeholder="BMI" onChange={handleChange} />
        <br /><br />

        <button type="submit">Predict</button>
      </form>

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Risk Score: {result.risk_score}</h3>
          <h4>Risk Level: {result.risk_level}</h4>

          <button onClick={goToDashboard} style={{ marginTop: "10px" }}>
            View Dashboard
          </button>
        </div>
      )}
    </div>
  );
}

export default Prediction;