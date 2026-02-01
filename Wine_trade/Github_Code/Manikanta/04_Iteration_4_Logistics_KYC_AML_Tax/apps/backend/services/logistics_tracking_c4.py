"""
Phase C4: Logistics & Condition Tracking
Tracks physical shipment state and condition during execution.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


def create_shipment(simulation_id: str, origin: str, destination: str, conn=None) -> Dict:
    """
    Create a shipment record for a simulation.
    
    Args:
        simulation_id: Simulation ID
        origin: Origin location
        destination: Destination location
        conn: Optional database connection
        
    Returns:
        dict: Created shipment record
    """
    should_close = False
    if conn is None:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not set")
        conn = psycopg2.connect(DATABASE_URL)
        should_close = True
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'shipments'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            logger.warning("shipments table does not exist. Run Phase C4 migration.")
            return {}
        
        shipment_id = str(uuid.uuid4())
        tracking_number = f'TRACK_{uuid.uuid4().hex[:8].upper()}'
        estimated_delivery = datetime.now() + timedelta(days=7)
        
        cursor.execute("""
            INSERT INTO shipments (
                id, simulation_id, tracking_number, origin_location, destination_location,
                status, estimated_delivery_date, carrier, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tracking_number) DO NOTHING
            RETURNING *
        """, (
            shipment_id,
            simulation_id,
            tracking_number,
            origin,
            destination,
            'PENDING',
            estimated_delivery,
            'SIMULATED_CARRIER',
            datetime.now()
        ))
        
        shipment = cursor.fetchone()
        conn.commit()
        
        if shipment:
            logger.info(f"Created shipment {tracking_number} for simulation {simulation_id}")
            return dict(shipment)
        
        return {}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating shipment: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        if should_close:
            conn.close()


def update_shipment_condition(shipment_id: str, conn=None) -> Dict:
    """
    Update condition snapshot for a shipment (simulated).
    
    Args:
        shipment_id: Shipment ID
        conn: Optional database connection
        
    Returns:
        dict: Condition snapshot record
    """
    should_close = False
    if conn is None:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not set")
        conn = psycopg2.connect(DATABASE_URL)
        should_close = True
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'condition_snapshots'
            ) as exists
        """)
        result = cursor.fetchone()
        if not result or not result['exists']:
            logger.warning("condition_snapshots table does not exist. Run Phase C4 migration.")
            return {}
        
        # Simulate condition metrics
        temperature = random.uniform(12.0, 18.0)  # Ideal wine storage temp
        humidity = random.uniform(50.0, 70.0)  # Ideal humidity
        shock_events = random.randint(0, 2)  # Simulated shock events
        
        # Calculate condition score (0-100)
        condition_score = 100.0
        if temperature < 10 or temperature > 20:
            condition_score -= 20
        if humidity < 40 or humidity > 80:
            condition_score -= 15
        condition_score -= shock_events * 10
        condition_score = max(0, min(100, condition_score))
        
        # Determine risk level
        if condition_score >= 80:
            risk_level = 'LOW'
        elif condition_score >= 60:
            risk_level = 'MEDIUM'
        elif condition_score >= 40:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        snapshot_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO condition_snapshots (
                id, shipment_id, temperature_celsius, humidity_percent,
                shock_events, condition_score, risk_level, snapshot_timestamp
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """, (
            snapshot_id,
            shipment_id,
            temperature,
            humidity,
            shock_events,
            condition_score,
            risk_level,
            datetime.now()
        ))
        
        snapshot = cursor.fetchone()
        conn.commit()
        
        if snapshot:
            logger.info(f"Created condition snapshot for shipment {shipment_id}: score={condition_score:.1f}, risk={risk_level}")
            return dict(snapshot)
        
        return {}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating shipment condition: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        if should_close:
            conn.close()


def get_shipment_timeline(simulation_id: str, conn=None) -> List[Dict]:
    """
    Get shipment timeline with condition snapshots for a simulation.
    
    Args:
        simulation_id: Simulation ID
        conn: Optional database connection
        
    Returns:
        list: List of shipment and condition records
    """
    should_close = False
    if conn is None:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not set")
        conn = psycopg2.connect(DATABASE_URL)
        should_close = True
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                s.*,
                json_agg(
                    json_build_object(
                        'id', cs.id,
                        'temperature', cs.temperature_celsius,
                        'humidity', cs.humidity_percent,
                        'shock_events', cs.shock_events,
                        'condition_score', cs.condition_score,
                        'risk_level', cs.risk_level,
                        'timestamp', cs.snapshot_timestamp
                    ) ORDER BY cs.snapshot_timestamp ASC
                ) FILTER (WHERE cs.id IS NOT NULL) as condition_snapshots
            FROM shipments s
            LEFT JOIN condition_snapshots cs ON s.id = cs.shipment_id
            WHERE s.simulation_id = %s
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """, (simulation_id,))
        
        shipments = cursor.fetchall()
        return [dict(ship) for ship in shipments]
        
    except Exception as e:
        logger.error(f"Error fetching shipment timeline: {e}", exc_info=True)
        return []
    finally:
        cursor.close()
        if should_close:
            conn.close()
