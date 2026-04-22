import Graph from "../components/Graph";

function Dashboard() {
  // Hardcoded test data (to eliminate all bugs)
  const data = [
    { name: "Day 1", risk: 60 },
    { name: "Day 2", risk: 70 },
    { name: "Day 3", risk: 80 },
    { name: "Day 4", risk: 65 },
  ];

  return (
    <div style={{ padding: "20px" }}>
      <h2>Dashboard</h2>

      <h3>Risk Score: 60</h3>
      <h4>Risk Level: Medium</h4>

      <Graph data={data} />
    </div>
  );
}

export default Dashboard;