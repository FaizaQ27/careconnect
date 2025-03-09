import { useState } from "react";
import axios from "axios";
import { BackendAPI } from "../Config";

const PredictionPage = () => {
  const [symptoms, setSymptoms] = useState("");
  const [disease, setDisease] = useState("");
  const [doctor, setDoctor] = useState([]); // Recommended doctors based on disease
  const [suggestedDoctors, setSuggestedDoctors] = useState([]); // Suggested doctors from MongoDB
  const [cure, setCure] = useState([]);
  const [riskLevel, setRiskLevel] = useState([]);

  const handleChange = (e) => {
    setSymptoms(e.target.value);
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post(`${BackendAPI}/predict`, {
        symptoms,
      });

      // Check if the response contains data and update state
      if (response.data.disease) {
        setDisease(response.data.disease);
        setDoctor(response.data.doctor); // Set recommended doctors based on disease
        setSuggestedDoctors(response.data.suggested_doctors); // Set suggested doctors from MongoDB
        setCure(response.data.cure);
        setRiskLevel(response.data.risk_levels);
      } else {
        console.error("No disease prediction returned.");
      }

      // Now store the prediction data in MongoDB
      const predictionData = {
        symptoms,
        disease: response.data.disease,
        doctor: response.data.doctor,
        suggested_doctors: response.data.suggested_doctors,
        cure: response.data.cure,
        risk_level: response.data.risk_levels,
      };

      await axios.post(
        "http://localhost:5000/store-prediction",
        predictionData,
        {
          withCredentials: true,
        }
      );

      console.log("Prediction data saved!");
    } catch (error) {
      console.error("Error fetching prediction or storing data:", error);
    }
  };

  return (
    <>
      <div className="mx-auto my-10 p-4 flex flex-col items-center justify-center gap-4">
        <h1 className="text-center text-2xl md:text-3xl lg:text-4xl font-bold my-4">
          Disease Prediction & Suggestions
        </h1>

        <textarea
          value={symptoms}
          onChange={handleChange}
          rows={10}
          placeholder="Enter symptoms (comma-seprated) here in the format : symptom 1, symptom 2, ..."
          className="border-black border-[2px] mt-2 p-2 w-fit min-w-[300px] md:min-w-[450px] lg:min-w-[550px] mx-auto resize-none"
        />

        <button
          onClick={handleSubmit}
          className="p-2 rounded-[7px] min-w-[95px] text-center hover:scale-105 bg-green-700 hover:bg-green-600 text-white font-bold text-xl md:text-2xl my-4"
        >
          Predict Disease
        </button>

        <div className="my-4">
          {disease && (
            <div className="mt-2 p-4 rounded-md my-4 shadow-md shadow-black/50 z-10 border-[1px] border-black">
              <p className="text-lg">
                <span className="font-bold mr-4">Predicted Disease:</span>{" "}
                {disease}
              </p>
            </div>
          )}

          {/* Recommended Doctors */}
          {doctor.length > 0 && (
            <div className="mt-2 p-4 rounded-md my-4 shadow-md shadow-black/50 z-10 border-[1px] border-black">
              <p className="text-lg font-bold">Required Doctor(s):</p>
              <ul className="list-disc ml-6">
                {doctor.map((doc, index) => (
                  <li key={index}>{doc}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggested Doctors from MongoDB */}
          {suggestedDoctors.length > 0 && (
            <div className="mt-2 p-4 rounded-md my-4 shadow-md shadow-black/50 z-10 border-[1px] border-black">
              <p className="text-lg font-bold">Suggested Doctors:</p>
              <ul className="list-disc ml-6">
                {suggestedDoctors.map((doctor, index) => (
                  <li key={index}>
                    <strong>{doctor.name}</strong> -{" "}
                    {doctor.specialist_category}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Cures */}
          {cure.length > 0 && (
            <div className="mt-2 p-4 rounded-md my-4 shadow-md shadow-black/50 z-10 border-[1px] border-black">
              <p className="text-lg font-bold">Possible Cures:</p>
              <ul className="list-disc ml-6">
                {cure.map((c, index) => (
                  <li key={index}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Risk Levels */}
          {riskLevel.length > 0 && (
            <div className="mt-2 p-4 rounded-md my-4 shadow-md shadow-black/50 z-10 border-[1px] border-black">
              <p className="text-lg font-bold">Risk Level:</p>
              <ul className="list-disc ml-6">
                {riskLevel.map((risk, index) => (
                  <li key={index}>{risk}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default PredictionPage;
