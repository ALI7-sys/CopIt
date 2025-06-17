'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import AuthForm from './AuthForm';
import FormInput from './FormInput';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const signupSchema = z.object({
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
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  name: z
    .string()
    .min(1, 'Name is required')
    .min(2, 'Name must be at least 2 characters')
    .max(50, 'Name cannot be more than 50 characters'),
  phone: z
    .string()
    .min(1, 'Phone number is required')
    .regex(
      /^\+?[\d\s-]{10,}$/,
      'Please provide a valid phone number'
    ),
});

type SignupFormData = z.infer<typeof signupSchema>;

export default function SignupForm() {
  const { signup } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: SignupFormData) => {
    try {
      setIsLoading(true);
      setError(null);
      await signup(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const isLoadingState = isLoading || isSubmitting;

  return (
    <AuthForm
      title="Create your account"
      subtitle="Join us today! Fill in your details to get started."
      footerText="Already have an account?"
      footerLink={{ text: 'Sign in', href: '/login' }}
    >
      <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 gap-6">
          <FormInput
            id="email"
            type="email"
            label="Email address"
            autoComplete="email"
            error={errors.email?.message}
            disabled={isLoadingState}
            {...register('email')}
          />

          <FormInput
            id="password"
            type="password"
            label="Password"
            autoComplete="new-password"
            error={errors.password?.message}
            disabled={isLoadingState}
            {...register('password')}
          />

          <FormInput
            id="name"
            type="text"
            label="Full name"
            autoComplete="name"
            error={errors.name?.message}
            disabled={isLoadingState}
            {...register('name')}
          />

          <FormInput
            id="phone"
            type="tel"
            label="Phone number"
            autoComplete="tel"
            error={errors.phone?.message}
            disabled={isLoadingState}
            {...register('phone')}
          />
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoadingState}
            className={`
              w-full flex justify-center items-center py-2 px-4 border border-transparent
              rounded-md shadow-sm text-sm font-medium text-white
              bg-luxury-gray-700 hover:bg-luxury-gray-800 focus:outline-none
              focus:ring-2 focus:ring-offset-2 focus:ring-luxury-gray-500
              transition-colors duration-200
              ${isLoadingState ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isLoadingState ? (
              <>
                <LoadingSpinner size="sm" color="white" className="mr-2" />
                Creating account...
              </>
            ) : (
              'Create account'
            )}
          </button>
        </div>
      </form>
    </AuthForm>
  );
} 