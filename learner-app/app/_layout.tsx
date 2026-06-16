import { useEffect } from "react";
import { Stack, useRouter, useSegments } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AuthProvider, useAuth } from "../context/AuthContext";

function NavigationGuard() {
  const { user, loading } = useAuth();
  const segments = useSegments();
  const router   = useRouter();

  useEffect(() => {
    if (loading) return;
    const inAuth = segments[0] === "(auth)";
    if (!user && !inAuth) router.replace("/(auth)/login");
    if (user  &&  inAuth) router.replace("/(tabs)");
  }, [user, loading, segments]);

  return null;
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <NavigationGuard />
      <StatusBar style="light" backgroundColor="#2563EB" />
      <Stack screenOptions={{ headerShown: false }} />
    </AuthProvider>
  );
}
