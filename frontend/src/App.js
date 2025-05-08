import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { Upload as UploadIcon } from '@mui/icons-material';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while analyzing the resume');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Rate My Resume
        </Typography>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <input
              accept=".pdf"
              style={{ display: 'none' }}
              id="resume-upload"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="resume-upload">
              <Button
                variant="contained"
                component="span"
                startIcon={<UploadIcon />}
              >
                Select Resume
              </Button>
            </label>
            {file && (
              <Typography variant="body1">
                Selected: {file.name}
              </Typography>
            )}
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze Resume'}
            </Button>
          </Box>
        </Paper>

        {error && (
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light' }}>
            <Typography color="error">{error}</Typography>
          </Paper>
        )}

        {analysis && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
              Resume Score: {analysis.score}/100
            </Typography>
            
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Metrics
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Word Count"
                  secondary={analysis.metrics.word_count}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Sentence Count"
                  secondary={analysis.metrics.sentence_count}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Action Verbs Found"
                  secondary={analysis.metrics.action_verbs_found}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Technical Skills Found"
                  secondary={analysis.metrics.technical_skills_found}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Passive Voice Sentences"
                  secondary={analysis.metrics.passive_voice_sentences}
                />
              </ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Strengths
            </Typography>
            <List>
              {analysis.strengths.map((strength, index) => (
                <ListItem key={index}>
                  <ListItemText primary={strength} />
                </ListItem>
              ))}
            </List>

            <Typography variant="h6" gutterBottom>
              Areas for Improvement
            </Typography>
            <List>
              {analysis.weaknesses.map((weakness, index) => (
                <ListItem key={index}>
                  <ListItemText primary={weakness} />
                </ListItem>
              ))}
            </List>

            <Typography variant="h6" gutterBottom>
              Suggestions
            </Typography>
            <List>
              {analysis.suggestions.map((suggestion, index) => (
                <ListItem key={index}>
                  <ListItemText primary={suggestion} />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App; 