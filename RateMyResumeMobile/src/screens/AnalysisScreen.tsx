import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../../App';
import axios from 'axios';
import * as FileSystem from 'expo-file-system';

type AnalysisScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Analysis'>;
  route: RouteProp<RootStackParamList, 'Analysis'>;
};

export default function AnalysisScreen({ navigation, route }: AnalysisScreenProps) {
  const [progress, setProgress] = useState(0);
  const { fileUri } = route.params;

  useEffect(() => {
    analyzeResume();
  }, []);

  const analyzeResume = async () => {
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', {
        uri: fileUri,
        type: 'application/pdf',
        name: 'resume.pdf',
      } as any);

      // Upload and analyze
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          setProgress(percentCompleted);
        },
      });

      // Navigate to results screen
      navigation.replace('Results', { analysisData: response.data });
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to analyze resume. Please try again.',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.title}>Analyzing Your Resume</Text>
        <Text style={styles.progress}>{progress}%</Text>
        <Text style={styles.subtitle}>
          Please wait while we analyze your resume...
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  progress: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#2196F3',
    marginVertical: 20,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
}); 