import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Get the pathname of the request
  const path = request.nextUrl.pathname;

  // Define public paths that don't require authentication
  const isPublicPath = path === '/login' || path === '/signup' || path === '/';

  // Get the token from the cookies
  const token = request.cookies.get('token')?.value || '';

  // Redirect logic
  if (isPublicPath && token) {
    // If user is logged in and tries to access public paths, redirect to dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  if (!isPublicPath && !token) {
    // If user is not logged in and tries to access protected paths, redirect to login
    return NextResponse.redirect(new URL('/login', request.url));
  }

  const isAdminPath = path.startsWith('/admin');
  const isLoginPath = path === '/admin/login';

  // If trying to access admin routes without being logged in
  if (isAdminPath && !token && !isLoginPath) {
    return NextResponse.redirect(new URL('/admin/login', request.url));
  }

  // If trying to access login page while already logged in
  if (isLoginPath && token) {
    return NextResponse.redirect(new URL('/admin', request.url));
  }

  return NextResponse.next();
}

// Configure which paths the middleware should run on
export const config = {
  matcher: [
    '/',
    '/login',
    '/signup',
    '/dashboard/:path*',
    '/api/:path*',
    '/admin/:path*',
  ],
}; 