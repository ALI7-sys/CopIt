import React from 'react';
import { Container, Typography } from '@mui/material';
import QRCodeGenerator from '../components/QRCodeGenerator';

const QRCodePage: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        QR Code Generator
      </Typography>
      <Typography variant="body1" paragraph align="center">
        Generate a QR code for the current page URL
      </Typography>
      <QRCodeGenerator />
    </Container>
  );
};

export default QRCodePage; 