'use client';

import React from 'react';
import Link from 'next/link';

interface FooterLink {
  href: string;
  text: string;
}

interface AuthFormProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footerText: string;
  footerLink: FooterLink;
}

export default function AuthForm({
  title,
  subtitle,
  children,
  footerText,
  footerLink,
}: AuthFormProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-luxury-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-luxury-gray-900">
            {title}
          </h2>
          <p className="mt-2 text-center text-sm text-luxury-gray-600">
            {subtitle}
          </p>
        </div>
        <div className="mt-8 bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {children}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-luxury-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-luxury-gray-500">
                  {footerText}{' '}
                  <Link
                    href={footerLink.href}
                    className="font-medium text-luxury-gray-700 hover:text-luxury-gray-900"
                  >
                    {footerLink.text}
                  </Link>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 