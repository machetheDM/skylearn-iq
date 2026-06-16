import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../context/AuthContext";
import { C } from "../../constants/colors";

export default function ProfileScreen() {
  const { user, signOut } = useAuth();

  function handleSignOut() {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      { text: "Sign Out", style: "destructive", onPress: signOut },
    ]);
  }

  return (
    <View style={s.container}>
      {/* Avatar */}
      <View style={s.avatarSection}>
        <View style={s.avatar}>
          <Text style={s.avatarText}>
            {user?.full_name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
          </Text>
        </View>
        <Text style={s.name}>{user?.full_name}</Text>
        <Text style={s.role}>Learner · SKYLearn IQ</Text>
      </View>

      {/* Info cards */}
      <View style={s.section}>
        <InfoRow icon="school-outline"     label="Organisation" value="SKYLearn-Innovation NPO" />
        <InfoRow icon="person-outline"     label="Role"         value="Learner" />
        <InfoRow icon="checkmark-shield-outline" label="Platform"   value="SKYLearn IQ — AI-Powered Learning" />
      </View>

      {/* Sign out */}
      <TouchableOpacity style={s.signOutBtn} onPress={handleSignOut}>
        <Ionicons name="log-out-outline" size={20} color={C.danger} />
        <Text style={s.signOutText}>Sign Out</Text>
      </TouchableOpacity>

      <Text style={s.footer}>SKYLearn-Innovation NPO · v1.0.0</Text>
    </View>
  );
}

function InfoRow({ icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <View style={ir.row}>
      <Ionicons name={icon} size={20} color={C.primary} />
      <View style={{ flex: 1 }}>
        <Text style={ir.label}>{label}</Text>
        <Text style={ir.value}>{value}</Text>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container:     { flex: 1, backgroundColor: C.bg },
  avatarSection: { backgroundColor: C.primary, alignItems: "center", paddingVertical: 40, paddingBottom: 48 },
  avatar:        { width: 80, height: 80, borderRadius: 40, backgroundColor: "rgba(255,255,255,0.2)", alignItems: "center", justifyContent: "center", marginBottom: 12 },
  avatarText:    { fontSize: 28, fontWeight: "800", color: C.white },
  name:          { fontSize: 20, fontWeight: "800", color: C.white },
  role:          { fontSize: 13, color: "#BFDBFE", marginTop: 4 },
  section:       { backgroundColor: C.card, marginHorizontal: 16, marginTop: -20, borderRadius: 16, padding: 4, borderWidth: 1, borderColor: C.border, elevation: 4, shadowColor: "#000", shadowOpacity: 0.08, shadowRadius: 10 },
  signOutBtn:    { flexDirection: "row", alignItems: "center", gap: 10, margin: 16, marginTop: 24, padding: 16, backgroundColor: "#FEF2F2", borderRadius: 12, borderWidth: 1, borderColor: "#FECACA" },
  signOutText:   { color: C.danger, fontWeight: "700", fontSize: 15 },
  footer:        { textAlign: "center", color: C.textMuted, fontSize: 12, marginTop: 16 },
});
const ir = StyleSheet.create({
  row:   { flexDirection: "row", alignItems: "center", gap: 14, padding: 14, borderBottomWidth: 1, borderBottomColor: C.border },
  label: { fontSize: 11, color: C.textMuted, marginBottom: 2 },
  value: { fontSize: 14, color: C.textPrimary, fontWeight: "600" },
});
