'use client';

import { useState } from 'react';
import { login, register } from '@/lib/api';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const res = isRegister
        ? await register(email, name, password)
        : await login(email, password);
      localStorage.setItem('token', res.data.access_token);
      window.location.href = '/';
    } catch {
      setError('Authentication failed. Please check your credentials.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20">
      <div className="bg-white rounded-lg shadow p-8">
        <h1 className="text-2xl font-bold mb-6">
          {isRegister ? 'Create Account' : 'Sign In'}
        </h1>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          {isRegister && (
            <input
              type="text"
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border rounded px-3 py-2"
              required
            />
          )}
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          <button
            type="submit"
            className="w-full bg-scout-600 text-white py-2 rounded hover:bg-scout-700"
          >
            {isRegister ? 'Register' : 'Sign In'}
          </button>
        </form>
        <p className="text-sm text-center mt-4">
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="text-scout-600 hover:underline"
          >
            {isRegister ? 'Already have an account? Sign in' : 'Need an account? Register'}
          </button>
        </p>
      </div>
    </div>
  );
}
