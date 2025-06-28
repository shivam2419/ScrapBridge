import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import { Suspense, lazy } from "react";

// Common components
import AutoRefreshToken from "./components/AutoRefreshToken.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import ErrorBoundary from "./components/ErrorBoundary.jsx"; // adjust the path as needed
import { Navbar } from "./components/Navbar.jsx";
import { Footer } from "./components/Footer.jsx";
import Home from './components/Home.jsx';
import Efacility from './components/Efacility.jsx';
import ScrapRequestDetails from "./components/ScrapRequestDetails.jsx";
import loader from '../src/assets/loader.gif';
// Lazy-loaded components
const Signup = lazy(() => import("./components/Signup.jsx"));
const Login = lazy(() => import("./components/Login.jsx"));
const About = lazy(() => import("./components/About.jsx"));
const Education = lazy(() => import("./components/Education.jsx"));
const Contact = lazy(() => import("./components/Contact.jsx"));
const ImageClassifier = lazy(() => import("./components/ImageClassifier.jsx"));
const Notifications = lazy(() => import("./components/Notifications.jsx"));
const Price_List = lazy(() => import("./components/Price_List.jsx"));
const Recycle_Form = lazy(() => import("./components/Recycle_Form.jsx"));
const Profile = lazy(() => import("./components/Profile.jsx"));
const ScrapCollectorDashboard = lazy(() =>
  import("./components/ScrapCollectorDashboard.jsx")
);
const ScrapCollectorOrders = lazy(() =>
  import("./components/ScrapCollectorOrders.jsx")
);
// const ScrapRequestDetails = lazy(() =>
//   import("./components/ScrapRequestDetails.jsx")
// );
const PendingPayments = lazy(() => import("./components/PendingPayments.jsx"));
const Payment = lazy(() => import("./components/Payment.jsx"));
const ScrapCollectorProfile = lazy(() =>
  import("./components/ScrapCollectorProfile.jsx")
);
const RecyclerProfile = lazy(() => import("./components/RecyclerProfile.jsx"));
const ScrapOrders = lazy(() => import("./components/ScrapOrders.jsx"));

function AppContent() {
  const location = useLocation();
  const hideLayoutFor = [
    "/scrap-collector",
    "/orders",
    "/pending-order",
    "/scrap-collector/profile",
    "/profile",
  ];
  const shouldHideLayout =
    hideLayoutFor.includes(location.pathname) ||
    location.pathname.startsWith("/scraprequest-details/") ||
    location.pathname.startsWith("/payment/");

  return (
    <>
      <AutoRefreshToken />
      {!shouldHideLayout && <Navbar />}
      <ErrorBoundary>
        <Suspense fallback={<center><img src={loader} alt="" /> <br />Loading Content...</center>}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/login" element={<Login />} />
            <Route path="/about" element={<About />} />
            <Route path="/education" element={<Education />} />
            <Route path="/contact" element={<Contact />} />
            {/* <Route path="/classify-image" element={<ImageClassifier />} /> */}
            <Route path="/e-facility" element={<Efacility />} />
            <Route
              path="/notification"
              element={
                <ProtectedRoute>
                  <Notifications />
                </ProtectedRoute>
              }
            />
            <Route path="/prices" element={<Price_List />} />
            <Route
              path="/recycle_main/:user_id"
              element={
                <ProtectedRoute>
                  <Recycle_Form />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/scrap-orders"
              element={
                <ProtectedRoute>
                  <ScrapOrders />
                </ProtectedRoute>
              }
            />
            <Route
              path="/scrap-collector"
              element={
                <ProtectedRoute>
                  <ScrapCollectorDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recycler-profile/:userId"
              element={<RecyclerProfile />}
            />
            <Route
              path="/orders"
              element={
                <ProtectedRoute>
                  <ScrapCollectorOrders />
                </ProtectedRoute>
              }
            />
            <Route
              path="/scraprequest-details/:orderId"
              element={
                <ProtectedRoute>
                  <ScrapRequestDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pending-order"
              element={
                <ProtectedRoute>
                  <PendingPayments />
                </ProtectedRoute>
              }
            />
            <Route
              path="/payment/:order_id/:user/"
              element={
                <ProtectedRoute>
                  <Payment />
                </ProtectedRoute>
              }
            />
            <Route
              path="/scrap-collector/profile/"
              element={
                <ProtectedRoute>
                  <ScrapCollectorProfile />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Suspense>
      </ErrorBoundary>

      {!shouldHideLayout && <Footer />}
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
