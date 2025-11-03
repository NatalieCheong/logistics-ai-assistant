import React from 'react';
import { useParams } from 'react-router-dom';

const ShipmentDetail: React.FC = () => {
  const { id } = useParams();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">Shipment Detail</h1>
      <p>Tracking ID: {id}</p>
      <p>This page is under construction.</p>
    </div>
  );
};

export default ShipmentDetail;


