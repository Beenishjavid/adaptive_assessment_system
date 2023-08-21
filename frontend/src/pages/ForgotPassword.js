import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';

const ForgotPassword = () => {
  const navigate = useNavigate();
  
  // Step management
  const [currentStep, setCurrentStep] = useState(1); // 1: Email, 2: OTP, 3: New Password
  
  // Form states
  const [email, setEmail] = useState('');
  const [otpCode, setOtpCode] = useState(['', '', '', '', '', '']);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [otpTimer, setOtpTimer] = useState(0);
  
  // Refs for OTP inputs
  const otpRefs = [
    useRef(null), useRef(null), useRef(null), 
    useRef(null), useRef(null), useRef(null)
  ];

  // Step 1: Send OTP to email
  const handleSendOTP = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/auth/password-reset/send-otp/', { email });
      setCurrentStep(2);
      startOTPTimer();
      toast.success('OTP sent to your email address!');
    } catch (error) {
      console.error('Send OTP error:', error);
      
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.data?.email) {
        setError(error.response.data.email[0]);
      } else {
        setError('Failed to send OTP. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify OTP
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    
    const otpString = otpCode.join('');
    
    if (otpString.length !== 6) {
      setError('Please enter the complete 6-digit OTP');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/auth/password-reset/verify-otp/', {
        email,
        otp_code: otpString
      });
      
      if (response.data.verified) {
        setCurrentStep(3);
        toast.success('OTP verified successfully!');
      }
    } catch (error) {
      console.error('Verify OTP error:', error);
      
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Invalid OTP. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Reset Password
  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (!newPassword || !confirmPassword) {
      setError('Please fill in both password fields');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/auth/password-reset/reset-with-otp/', {
        email,
        otp_code: otpCode.join(''),
        new_password: newPassword,
        new_password_confirm: confirmPassword
      });
      
      toast.success('Password reset successfully!');
      navigate('/login', { 
        state: { 
          message: 'Password reset successfully. Please login with your new password.' 
        }
      });
    } catch (error) {
      console.error('Reset password error:', error);
      
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.data?.new_password) {
        setError(error.response.data.new_password[0]);
      } else {
        setError('Failed to reset password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // OTP Input handling
  const handleOTPChange = (index, value) => {
    if (value.length > 1) return; // Prevent multiple characters
    
    const newOtpCode = [...otpCode];
    newOtpCode[index] = value;
    setOtpCode(newOtpCode);
    setError('');

    // Auto-focus next input
    if (value && index < 5) {
      otpRefs[index + 1].current?.focus();
    }
  };

  const handleOTPKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otpCode[index] && index > 0) {
      otpRefs[index - 1].current?.focus();
    }
  };

  const handleOTPPaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, 6);
    if (/^\d+$/.test(pastedData)) {
      const newOtpCode = pastedData.split('').concat(['', '', '', '', '', '']).slice(0, 6);
      setOtpCode(newOtpCode);
      setError('');
      
      // Focus the next empty input or last input
      const nextIndex = Math.min(pastedData.length, 5);
      otpRefs[nextIndex].current?.focus();
    }
  };

  // Timer for OTP expiry
  const startOTPTimer = () => {
    setOtpTimer(600); // 10 minutes in seconds
    const timer = setInterval(() => {
      setOtpTimer((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleResendOTP = () => {
    setCurrentStep(1);
    setOtpCode(['', '', '', '', '', '']);
    setError('');
  };

  // Step indicator component
  const StepIndicator = ({ currentStep }) => (
    <div className="flex items-center justify-center mb-8">
      <div className="flex items-center space-x-4">
        {[1, 2, 3].map((step) => (
          <div key={step} className="flex items-center">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
              currentStep >= step 
                ? 'bg-primary-600 border-primary-600 text-white' 
                : 'border-gray-300 text-gray-300'
            }`}>
              {currentStep > step ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <span className="text-sm font-medium">{step}</span>
              )}
            </div>
            {step < 3 && (
              <div className={`w-12 h-0.5 ${
                currentStep > step ? 'bg-primary-600' : 'bg-gray-300'
              }`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        
        {/* Step Indicator */}
        <StepIndicator currentStep={currentStep} />

        {/* Step 1: Enter Email */}
        {currentStep === 1 && (
          <div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-600">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Reset Password
              </h2>
              <p className="mt-2 text-center text-sm text-gray-600">
                Enter your email address to receive an OTP
              </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleSendOTP}>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className={`form-input mt-1 ${error ? 'border-red-500' : ''}`}
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setError('');
                  }}
                />
                {error && (
                  <p className="mt-1 text-sm text-red-600">{error}</p>
                )}
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  {loading ? (
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : null}
                  Send OTP
                </button>
              </div>

              <div className="text-center">
                <Link
                  to="/login"
                  className="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-200"
                >
                  Back to login
                </Link>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: Enter OTP */}
        {currentStep === 2 && (
          <div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-600">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Enter OTP
              </h2>
              <p className="mt-2 text-center text-sm text-gray-600">
                We've sent a 6-digit code to
              </p>
              <p className="mt-1 text-center text-sm font-medium text-primary-600">
                {email}
              </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleVerifyOTP}>
              <div>
                <label className="block text-sm font-medium text-gray-700 text-center mb-4">
                  Enter 6-Digit OTP
                </label>
                <div className="flex justify-center space-x-3">
                  {otpCode.map((digit, index) => (
                    <input
                      key={index}
                      ref={otpRefs[index]}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      className={`w-12 h-12 text-center text-lg font-semibold border-2 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                        error ? 'border-red-500' : 'border-gray-300'
                      }`}
                      value={digit}
                      onChange={(e) => handleOTPChange(index, e.target.value.replace(/\D/g, ''))}
                      onKeyDown={(e) => handleOTPKeyDown(index, e)}
                      onPaste={handleOTPPaste}
                    />
                  ))}
                </div>
                {error && (
                  <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
                )}
                
                {otpTimer > 0 && (
                  <p className="mt-3 text-sm text-gray-500 text-center">
                    Code expires in: <span className="font-semibold">{formatTime(otpTimer)}</span>
                  </p>
                )}
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading || otpCode.join('').length !== 6}
                  className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  {loading ? (
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : null}
                  Verify OTP
                </button>
              </div>

              <div className="flex justify-between text-sm">
                <button
                  type="button"
                  onClick={handleResendOTP}
                  className="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-200"
                >
                  Resend OTP
                </button>
                <Link
                  to="/login"
                  className="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-200"
                >
                  Back to login
                </Link>
              </div>
            </form>
          </div>
        )}

        {/* Step 3: Set New Password */}
        {currentStep === 3 && (
          <div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-600">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1721 9z" />
                </svg>
              </div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Set New Password
              </h2>
              <p className="mt-2 text-center text-sm text-gray-600">
                Create a strong, secure password
              </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleResetPassword}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
                    New Password
                  </label>
                  <input
                    id="newPassword"
                    name="newPassword"
                    type="password"
                    required
                    className={`form-input mt-1 ${error ? 'border-red-500' : ''}`}
                    placeholder="Enter new password"
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value);
                      setError('');
                    }}
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    required
                    className={`form-input mt-1 ${error ? 'border-red-500' : ''}`}
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      setError('');
                    }}
                  />
                </div>

                {error && (
                  <p className="mt-1 text-sm text-red-600">{error}</p>
                )}

                <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                  <div className="text-sm text-blue-700">
                    <strong>Password requirements:</strong>
                    <ul className="mt-1 list-disc pl-5 space-y-1">
                      <li>At least 8 characters long</li>
                      <li>Mix of uppercase and lowercase letters</li>
                      <li>At least one number</li>
                      <li>At least one special character</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  {loading ? (
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : null}
                  Reset Password
                </button>
              </div>

              <div className="text-center">
                <Link
                  to="/login"
                  className="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-200"
                >
                  Back to login
                </Link>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default ForgotPassword;
