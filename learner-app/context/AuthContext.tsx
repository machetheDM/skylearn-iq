"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

const TOKEN_KEY = "skylearn_learner_token";
const USER_KEY  = "skylearn_learner_user";

type AuthUser = {
  user_id: number;
  full_name: string;
  role: string;
  access_token: string;
};

type AuthCtx = {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  signIn: (data: AuthUser) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthCtx>({} as AuthCtx);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser]     = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const stored = await AsyncStorage.getItem(USER_KEY);
        if (stored) setUser(JSON.parse(stored));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const signIn = async (data: AuthUser) => {
    await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
    await AsyncStorage.setItem(USER_KEY,  JSON.stringify(data));
    setUser(data);
  };

  const signOut = async () => {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token: user?.access_token ?? null, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
