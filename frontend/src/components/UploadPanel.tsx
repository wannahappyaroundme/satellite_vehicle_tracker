import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { Upload, Camera, MapPin, Image as ImageIcon, CheckCircle, AlertCircle } from 'lucide-react';
import { VehicleData } from '../types';
import { uploadImageForDetection } from '../services/api';

const PanelContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
`;

const Section = styled.div`
  margin-bottom: 25px;
`;

const SectionTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const UploadArea = styled.div<{ isDragOver: boolean }>`
  border: 2px dashed ${props => props.isDragOver ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.3)'};
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  background: ${props => props.isDragOver ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.05)'};
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    border-color: rgba(255,255,255,0.6);
    background: rgba(255,255,255,0.1);
  }
`;

const UploadIcon = styled.div`
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.7;
`;

const UploadText = styled.div`
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
`;

const UploadSubtext = styled.div`
  font-size: 14px;
  opacity: 0.7;
`;

const InputGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 6px;
  background: rgba(255,255,255,0.1);
  color: white;
  font-size: 14px;

  &::placeholder {
    color: rgba(255,255,255,0.6);
  }

  &:focus {
    outline: none;
    border-color: rgba(255,255,255,0.5);
    background: rgba(255,255,255,0.15);
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 12px;
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255,255,255,0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const PreviewContainer = styled.div`
  margin-top: 20px;
  text-align: center;
`;

const PreviewImage = styled.img`
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
`;

const StatusMessage = styled.div<{ type: 'success' | 'error' | 'info' }>`
  padding: 10px;
  border-radius: 6px;
  margin-top: 15px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: ${props => 
    props.type === 'success' ? 'rgba(39, 174, 96, 0.2)' :
    props.type === 'error' ? 'rgba(231, 76, 60, 0.2)' :
    'rgba(52, 152, 219, 0.2)'
  };
  border: 1px solid ${props => 
    props.type === 'success' ? 'rgba(39, 174, 96, 0.3)' :
    props.type === 'error' ? 'rgba(231, 76, 60, 0.3)' :
    'rgba(52, 152, 219, 0.3)'
  };
  color: ${props => 
    props.type === 'success' ? '#27ae60' :
    props.type === 'error' ? '#e74c3c' :
    '#3498db'
  };
`;

const DetectionResults = styled.div`
  margin-top: 20px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
`;

const DetectionItem = styled.div`
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  font-size: 14px;

  &:last-child {
    border-bottom: none;
  }
`;

interface UploadPanelProps {
  onVehicleDetected: (vehicles: VehicleData[]) => void;
  onLoadingChange: (loading: boolean) => void;
}

const UploadPanel: React.FC<UploadPanelProps> = ({
  onVehicleDetected,
  onLoadingChange
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [coordinates, setCoordinates] = useState({
    lat: 40.7128,
    lng: -74.0060,
    zoom: 13
  });
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error' | 'info', message: string } | null>(null);
  const [detectionResults, setDetectionResults] = useState<VehicleData[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file: File) => {
    if (file.type.startsWith('image/')) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setUploadStatus(null);
      setDetectionResults([]);
    } else {
      setUploadStatus({ type: 'error', message: 'Please select an image file' });
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ type: 'error', message: 'Please select an image first' });
      return;
    }

    onLoadingChange(true);
    setUploadStatus({ type: 'info', message: 'Processing image...' });

    try {
      // Convert file to base64
      const base64 = await fileToBase64(selectedFile);
      
      // Upload for detection
      const results = await uploadImageForDetection({
        image: base64,
        coordinates: coordinates
      });

      onVehicleDetected(results.vehicles);
      setDetectionResults(results.vehicles);
      setUploadStatus({ 
        type: 'success', 
        message: `Successfully detected ${results.detections} vehicles` 
      });

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({ 
        type: 'error', 
        message: 'Failed to process image. Please try again.' 
      });
    } finally {
      onLoadingChange(false);
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  };

  const clearUpload = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setUploadStatus(null);
    setDetectionResults([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <PanelContainer>
      <Section>
        <SectionTitle>
          <Camera size={16} />
          Upload Satellite Image
        </SectionTitle>
        
        <UploadArea
          isDragOver={isDragOver}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <UploadIcon>
            <ImageIcon size={48} />
          </UploadIcon>
          <UploadText>Drop image here or click to browse</UploadText>
          <UploadSubtext>Supports JPG, PNG, GIF formats</UploadSubtext>
        </UploadArea>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />

        {previewUrl && (
          <PreviewContainer>
            <PreviewImage src={previewUrl} alt="Preview" />
          </PreviewContainer>
        )}
      </Section>

      <Section>
        <SectionTitle>
          <MapPin size={16} />
          Image Location
        </SectionTitle>
        
        <InputGroup>
          <Label>Latitude</Label>
          <Input
            type="number"
            step="any"
            value={coordinates.lat}
            onChange={(e) => setCoordinates(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
            placeholder="40.7128"
          />
        </InputGroup>

        <InputGroup>
          <Label>Longitude</Label>
          <Input
            type="number"
            step="any"
            value={coordinates.lng}
            onChange={(e) => setCoordinates(prev => ({ ...prev, lng: parseFloat(e.target.value) }))}
            placeholder="-74.0060"
          />
        </InputGroup>

        <InputGroup>
          <Label>Zoom Level</Label>
          <Input
            type="number"
            min="1"
            max="20"
            value={coordinates.zoom}
            onChange={(e) => setCoordinates(prev => ({ ...prev, zoom: parseInt(e.target.value) }))}
            placeholder="13"
          />
        </InputGroup>
      </Section>

      <Section>
        <Button onClick={handleUpload} disabled={!selectedFile}>
          <Upload size={16} />
          Process Image
        </Button>

        {selectedFile && (
          <Button 
            onClick={clearUpload}
            style={{ 
              background: 'rgba(231, 76, 60, 0.2)', 
              borderColor: 'rgba(231, 76, 60, 0.3)',
              marginTop: '10px'
            }}
          >
            Clear
          </Button>
        )}
      </Section>

      {uploadStatus && (
        <StatusMessage type={uploadStatus.type}>
          {uploadStatus.type === 'success' && <CheckCircle size={16} />}
          {uploadStatus.type === 'error' && <AlertCircle size={16} />}
          {uploadStatus.type === 'info' && <Upload size={16} />}
          {uploadStatus.message}
        </StatusMessage>
      )}

      {detectionResults.length > 0 && (
        <DetectionResults>
          <SectionTitle>
            <CheckCircle size={16} />
            Detection Results
          </SectionTitle>
          {detectionResults.map((vehicle) => (
            <DetectionItem key={vehicle.id}>
              <strong>{vehicle.type}</strong> - {(vehicle.confidence * 100).toFixed(1)}% confidence
              <br />
              <small>Detected at {new Date(vehicle.timestamp).toLocaleString()}</small>
            </DetectionItem>
          ))}
        </DetectionResults>
      )}
    </PanelContainer>
  );
};

export default UploadPanel;

