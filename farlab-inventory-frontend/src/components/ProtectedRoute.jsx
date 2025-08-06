// sr/components/ProtectedRoute.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import LoadingSpinner from "./LoadingSpinner";

export function ProtectedRoute({ children }) {
  const { currentUser, authLoading } = useAppContext();
  const location = useLocation();

  // 1. While the app is checking for an existing token, show a loading spinner.
  // This prevents a flicker from the login page to the protected content.
  if (authLoading) {
    return <LoadingSpinner />;
  }

  // 2. If loading is finished and there's no user, redirect to the login page.
  // Pass the users's original destination in the 'state' object.
  // This allows to redirect them back to the page they originally wanted
  // after they successfully log in.
  if (!currentUser) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 3. If loading is finished and a user exists, render the child components.
  // This means the user is authenticated and can acess the page.
  return children;
}

export default ProtectedRoute;
