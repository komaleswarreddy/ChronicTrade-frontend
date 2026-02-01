import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Public routes that don't require authentication
const publicRoutes = [
  '/',
  '/sign-in',
  '/register',
  '/api/auth',
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow public routes
  if (publicRoutes.some(route => pathname === route || pathname.startsWith(route))) {
    return NextResponse.next()
  }

  // Allow API routes - they handle auth internally
  if (pathname.startsWith('/api/')) {
    return NextResponse.next()
  }

  // For protected routes, check for refresh token cookie
  // Client-side components will handle redirect if needed
  const refreshToken = request.cookies.get('refresh_token')
  
  if (!refreshToken && !pathname.startsWith('/api/')) {
    // Redirect to sign-in if no refresh token
    // Note: This is a basic check - full auth is handled client-side
    if (!publicRoutes.some(route => pathname.startsWith(route))) {
      return NextResponse.redirect(new URL('/sign-in', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
  ],
}
