import React, { useEffect, useState } from "react";
import axios from "axios";
import { BackendAPI } from "../Config";

const DashboardPage = () => {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await axios.get(
          `${BackendAPI}/get-predictions`,
          {
            withCredentials: true,
          }
        );
        setPredictions(response.data.predictions);
      } catch (error) {
        console.error("Error fetching predictions:", error);
      }
    };

    fetchPredictions();
  }, []);

  return (
    <div className="flex flex-col md:flex-row items-center flex-wrap gap-4 m-4 p-4 md:m-8 lg:m-12">
      {predictions.length > 0 ? (
        predictions.map((prediction, index) => (
          <div
            key={index}
            className="bg-white p-6 rounded-lg shadow-lg shadow-black/50 border-black border-[2px] w-fit min-w-[250px] max-w-[325px] min-h-[300px]"
          >
            <p>
              <strong>User Entered Symptoms:</strong> {prediction.symptoms}
            </p>
            <p>
              <strong>Predicted Disease:</strong> {prediction.disease}
            </p>
            <p>
              <strong>Recommended Doctors:</strong>{" "}
              {prediction.doctor.join(", ")}
            </p>
            <p>
              <strong>Possible Cures:</strong> {prediction.cure.join(", ")}
            </p>
            <p>
              <strong>Risk Level:</strong> {prediction.risk_level.join(", ")}
            </p>
            <p>
              <strong>Time:</strong>{" "}
              {new Date(prediction.timestamp).toLocaleString()}
            </p>
          </div>
        ))
      ) : (
        <p>No predictions available.</p>
      )}
    </div>
  );
};

export default DashboardPage;
