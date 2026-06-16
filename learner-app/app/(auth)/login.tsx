import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ActivityIndicator, Alert,
} from "react-native";
import { useAuth } from "../../context/AuthContext";
import { API_URL } from "../../constants/api";
import { C } from "../../constants/colors";

export default function LoginScreen() {
  const { signIn } = useAuth();
  const [phone, setPhone]       = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);

  async function handleLogin() {
    if (!phone || !password) {
      Alert.alert("Required", "Please enter your phone number and password.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: phone.trim(), password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail ?? "Login failed");
      await signIn(data);
    } catch (e: any) {
      Alert.alert("Login Failed", e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={s.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      {/* Header */}
      <View style={s.header}>
        <Text style={s.logo}>🧠 SKYLearn IQ</Text>
        <Text style={s.tagline}>AI-Powered Learning Platform</Text>
        <Text style={s.sub}>Sign in to access your assessments</Text>
      </View>

      {/* Form */}
      <View style={s.card}>
        <Text style={s.label}>Phone Number</Text>
        <TextInput
          style={s.input}
          placeholder="+27710000001"
          placeholderTextColor={C.textMuted}
          keyboardType="phone-pad"
          autoComplete="tel"
          value={phone}
          onChangeText={setPhone}
        />

        <Text style={[s.label, { marginTop: 16 }]}>Password</Text>
        <TextInput
          style={s.input}
          placeholder="Your password"
          placeholderTextColor={C.textMuted}
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <TouchableOpacity
          style={[s.btn, loading && { opacity: 0.6 }]}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading
            ? <ActivityIndicator color={C.white} />
            : <Text style={s.btnText}>Sign In</Text>
          }
        </TouchableOpacity>
      </View>

      <Text style={s.footer}>SKYLearn-Innovation NPO · For learners only</Text>
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  container:  { flex: 1, backgroundColor: C.primary, justifyContent: "center", paddingHorizontal: 24 },
  header:     { alignItems: "center", marginBottom: 32 },
  logo:       { fontSize: 32, fontWeight: "800", color: C.white, marginBottom: 6 },
  tagline:    { fontSize: 14, color: "#BFDBFE", fontWeight: "600", letterSpacing: 0.5 },
  sub:        { fontSize: 13, color: "#93C5FD", marginTop: 4 },
  card:       { backgroundColor: C.white, borderRadius: 20, padding: 24, shadowColor: "#000", shadowOpacity: 0.15, shadowRadius: 20, elevation: 8 },
  label:      { fontSize: 13, fontWeight: "600", color: C.textSecondary, marginBottom: 6 },
  input:      { borderWidth: 1.5, borderColor: C.border, borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, fontSize: 15, color: C.textPrimary, backgroundColor: C.bg },
  btn:        { backgroundColor: C.primary, borderRadius: 12, paddingVertical: 14, alignItems: "center", marginTop: 24 },
  btnText:    { color: C.white, fontWeight: "700", fontSize: 16 },
  footer:     { textAlign: "center", color: "#BFDBFE", fontSize: 12, marginTop: 24 },
});
