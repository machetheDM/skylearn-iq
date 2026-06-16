import React, { useEffect, useState, useRef } from "react";
import {
  View, Text, ScrollView, TouchableOpacity, TextInput,
  StyleSheet, Alert, ActivityIndicator,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../context/AuthContext";
import { API_URL } from "../../constants/api";
import { C } from "../../constants/colors";

type Option  = { id: number; text: string; order_num: number };
type Question = {
  id: number; text: string; q_type: string; marks: number;
  difficulty: string; concept_tag: string | null; order_num: number;
  options: Option[];
};
type Assessment = {
  id: number; title: string; description: string | null;
  total_marks: number; time_limit_min: number;
  subject: { name: string }; questions: Question[];
};
type Answers = Record<number, { option_id?: number; text?: string }>;

const DIFF_COLOR: Record<string, string> = {
  EASY: C.accent, MEDIUM: C.warning, HARD: C.danger,
};

export default function TakeAssessmentScreen() {
  const { id }         = useLocalSearchParams<{ id: string }>();
  const { token }      = useAuth();
  const router         = useRouter();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [sessionId, setSessionId]   = useState<number | null>(null);
  const [answers, setAnswers]       = useState<Answers>({});
  const [loading, setLoading]       = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft]     = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    (async () => {
      try {
        // Load assessment
        const aRes = await fetch(`${API_URL}/api/assessments/published`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const list: Assessment[] = await aRes.json();
        const a = list.find(x => x.id === Number(id));
        if (!a) { Alert.alert("Not found"); router.back(); return; }
        setAssessment(a);
        setTimeLeft(a.time_limit_min * 60);

        // Start session
        const sRes = await fetch(`${API_URL}/api/sessions/${id}/start`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
        const sData = await sRes.json();
        setSessionId(sData.session_id);
      } catch (e) {
        Alert.alert("Error", "Could not load assessment.");
      } finally {
        setLoading(false);
      }
    })();

    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [id]);

  useEffect(() => {
    if (timeLeft <= 0 || !sessionId) return;
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) { clearInterval(timerRef.current!); handleSubmit(true); return 0; }
        return t - 1;
      });
    }, 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [sessionId]);

  async function handleSubmit(auto = false) {
    if (!sessionId || !assessment) return;
    if (!auto) {
      const answered = Object.keys(answers).length;
      if (answered < assessment.questions.length) {
        const ok = await new Promise<boolean>(resolve =>
          Alert.alert("Incomplete", `You answered ${answered}/${assessment.questions.length} questions. Submit anyway?`, [
            { text: "Continue", onPress: () => resolve(false) },
            { text: "Submit", style: "destructive", onPress: () => resolve(true) },
          ])
        );
        if (!ok) return;
      }
    }
    setSubmitting(true);
    try {
      const payload = assessment.questions.map(q => ({
        question_id:        q.id,
        selected_option_id: answers[q.id]?.option_id ?? null,
        text_answer:        answers[q.id]?.text ?? null,
      }));
      const res = await fetch(`${API_URL}/api/sessions/${sessionId}/submit`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ answers: payload }),
      });
      if (!res.ok) throw new Error("Submit failed");
      router.replace(`/assessment/result/${sessionId}`);
    } catch {
      Alert.alert("Error", "Could not submit. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function formatTime(sec: number) {
    const m = Math.floor(sec / 60).toString().padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color={C.primary} />;
  if (!assessment) return null;

  const answered = Object.keys(answers).length;

  return (
    <View style={s.container}>
      {/* Fixed header */}
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={{ padding: 4 }}>
          <Ionicons name="close-outline" size={24} color={C.white} />
        </TouchableOpacity>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={s.headerTitle} numberOfLines={1}>{assessment.title}</Text>
          <Text style={s.headerSub}>{assessment.subject.name} · {assessment.total_marks} marks</Text>
        </View>
        <View style={[s.timer, timeLeft < 300 && { backgroundColor: C.danger }]}>
          <Ionicons name="time-outline" size={14} color={C.white} />
          <Text style={s.timerText}>{formatTime(timeLeft)}</Text>
        </View>
      </View>

      {/* Progress */}
      <View style={s.progressBar}>
        <View style={[s.progressFill, { width: `${(answered / assessment.questions.length) * 100}%` }]} />
      </View>
      <Text style={s.progressLabel}>{answered}/{assessment.questions.length} answered</Text>

      <ScrollView contentContainerStyle={{ padding: 16, gap: 20, paddingBottom: 100 }}>
        {assessment.questions
          .sort((a, b) => a.order_num - b.order_num)
          .map((q, idx) => (
            <View key={q.id} style={s.card}>
              {/* Question header */}
              <View style={s.qHeader}>
                <View style={s.qNum}><Text style={s.qNumText}>{idx + 1}</Text></View>
                <View style={s.qMeta}>
                  <View style={[s.diffBadge, { backgroundColor: DIFF_COLOR[q.difficulty] }]}>
                    <Text style={s.diffText}>{q.difficulty}</Text>
                  </View>
                  <Text style={s.marks}>{q.marks} mark{q.marks !== 1 ? "s" : ""}</Text>
                  {q.concept_tag && <Text style={s.tag}>{q.concept_tag}</Text>}
                </View>
              </View>

              <Text style={s.qText}>{q.text}</Text>

              {/* MCQ */}
              {q.q_type === "MCQ" && q.options.map(opt => {
                const selected = answers[q.id]?.option_id === opt.id;
                return (
                  <TouchableOpacity
                    key={opt.id}
                    style={[s.option, selected && s.optionSelected]}
                    onPress={() => setAnswers(prev => ({ ...prev, [q.id]: { option_id: opt.id } }))}
                  >
                    <View style={[s.optDot, selected && s.optDotSelected]} />
                    <Text style={[s.optText, selected && { color: C.primary, fontWeight: "600" }]}>{opt.text}</Text>
                  </TouchableOpacity>
                );
              })}

              {/* Short answer */}
              {(q.q_type === "SHORT_ANSWER" || q.q_type === "CODING") && (
                <TextInput
                  style={s.textInput}
                  placeholder={q.q_type === "CODING" ? "Write your code here..." : "Type your answer..."}
                  placeholderTextColor={C.textMuted}
                  multiline
                  numberOfLines={3}
                  value={answers[q.id]?.text ?? ""}
                  onChangeText={t => setAnswers(prev => ({ ...prev, [q.id]: { text: t } }))}
                />
              )}
            </View>
          ))}
      </ScrollView>

      {/* Submit button */}
      <View style={s.submitBar}>
        <TouchableOpacity
          style={[s.submitBtn, submitting && { opacity: 0.6 }]}
          onPress={() => handleSubmit(false)}
          disabled={submitting}
        >
          {submitting
            ? <ActivityIndicator color={C.white} />
            : <Text style={s.submitText}>Submit Assessment</Text>
          }
        </TouchableOpacity>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container:     { flex: 1, backgroundColor: C.bg },
  header:        { backgroundColor: C.primary, flexDirection: "row", alignItems: "center", paddingHorizontal: 16, paddingVertical: 14, paddingTop: 50 },
  headerTitle:   { color: C.white, fontWeight: "700", fontSize: 15 },
  headerSub:     { color: "#BFDBFE", fontSize: 11, marginTop: 1 },
  timer:         { flexDirection: "row", alignItems: "center", gap: 4, backgroundColor: "rgba(255,255,255,0.2)", paddingHorizontal: 10, paddingVertical: 5, borderRadius: 20 },
  timerText:     { color: C.white, fontWeight: "700", fontSize: 13 },
  progressBar:   { height: 4, backgroundColor: C.border },
  progressFill:  { height: 4, backgroundColor: C.accent },
  progressLabel: { fontSize: 11, color: C.textMuted, textAlign: "right", paddingRight: 16, paddingTop: 4, marginBottom: 4 },
  card:          { backgroundColor: C.card, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: C.border },
  qHeader:       { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 10 },
  qNum:          { width: 28, height: 28, borderRadius: 14, backgroundColor: C.primary, alignItems: "center", justifyContent: "center" },
  qNumText:      { color: C.white, fontWeight: "700", fontSize: 13 },
  qMeta:         { flex: 1, flexDirection: "row", flexWrap: "wrap", gap: 6, alignItems: "center" },
  diffBadge:     { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2 },
  diffText:      { color: C.white, fontSize: 10, fontWeight: "700" },
  marks:         { fontSize: 11, color: C.textMuted },
  tag:           { fontSize: 10, color: C.primary, backgroundColor: C.primaryLight, paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
  qText:         { fontSize: 14, color: C.textPrimary, lineHeight: 22, marginBottom: 14, fontWeight: "500" },
  option:        { flexDirection: "row", alignItems: "center", gap: 12, padding: 12, borderRadius: 10, borderWidth: 1.5, borderColor: C.border, marginBottom: 8, backgroundColor: C.bg },
  optionSelected:{ borderColor: C.primary, backgroundColor: "#EFF6FF" },
  optDot:        { width: 18, height: 18, borderRadius: 9, borderWidth: 2, borderColor: C.border },
  optDotSelected:{ borderColor: C.primary, backgroundColor: C.primary },
  optText:       { flex: 1, fontSize: 14, color: C.textPrimary },
  textInput:     { borderWidth: 1.5, borderColor: C.border, borderRadius: 10, padding: 12, fontSize: 14, color: C.textPrimary, minHeight: 80, textAlignVertical: "top", backgroundColor: C.bg },
  submitBar:     { position: "absolute", bottom: 0, left: 0, right: 0, padding: 16, backgroundColor: C.card, borderTopWidth: 1, borderTopColor: C.border },
  submitBtn:     { backgroundColor: C.primary, borderRadius: 12, paddingVertical: 16, alignItems: "center" },
  submitText:    { color: C.white, fontWeight: "700", fontSize: 16 },
});
