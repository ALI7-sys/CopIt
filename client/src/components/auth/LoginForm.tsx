'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import AuthForm from './AuthForm';
import FormInput from './FormInput';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { toast } from '@/lib/toast';

const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .regex(
      /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
      'Please provide a valid email'
    ),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginForm() {
  const { login, loading } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const isLoadingState = loading || isSubmitting;

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      await login(data.email, data.password);
      toast.success('Successfully logged in!');
      router.push('/');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to login';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  return (
    <AuthForm
      title="Welcome back"
      subtitle="Sign in to your account"
      footerText="Don't have an account?"
      footerLink={{ text: 'Sign up', href: '/signup' }}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        <FormInput
          label="Email"
          type="email"
          error={errors.email?.message}
          disabled={isLoadingState}
          {...register('email')}
        />

        <FormInput
          label="Password"
          type="password"
          error={errors.password?.message}
          disabled={isLoadingState}
          {...register('password')}
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 text-luxury-gray-700 focus:ring-luxury-gray-500 border-luxury-gray-300 rounded"
              disabled={isLoadingState}
            />
            <label
              htmlFor="remember-me"
              className="ml-2 block text-sm text-luxury-gray-900"
            >
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <a
              href="/forgot-password"
              className="font-medium text-luxury-gray-700 hover:text-luxury-gray-900"
            >
              Forgot your password?
            </a>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoadingState}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-luxury-gray-700 hover:bg-luxury-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-luxury-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoadingState ? (
            <LoadingSpinner size="sm" color="white" />
          ) : (
            'Sign in'
          )}
        </button>
      </form>
    </AuthForm>
  );
} 