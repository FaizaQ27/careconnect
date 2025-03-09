import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./Components/Navbar";
import HomePage from "./Pages/HomePage";
import Signup from "./Pages/Signup";
import Login from "./Pages/Login";
import ProfilePage from "./Pages/ProfilePage";
import PredictionPage from "./Pages/PredictionPage";
import AvailableDoctorsPage from "./Pages/AvailableDoctorsPage";
import ProtectedRoute from "./Components/ProtectedRoute";
import Footer from "./Components/Footer";
import AboutPage from "./Pages/AboutPage";
import AIMetricsPage from "./Pages/AIMetricsPage";
import DashboardPage from "./Pages/DashboardPage";

const App = () => {
  return (
    <>
      <Navbar />
      <div className="min-h-[125vh]">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/prediction"
            element={
              <ProtectedRoute>
                <PredictionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/available-doctors"
            element={
              <ProtectedRoute>
                <AvailableDoctorsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          <Route path="/ai-metrics" element={<AIMetricsPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </div>
      <div className="mt-32">
        <Footer />
      </div>
    </>
  );
};

export default App;
