/**
 * Attack types - Attack simulation scenarios
 */

import { Timestamps, Metadata, PaginatedResponse } from './common';

/**
 * Attack entity - Simulated attack scenario
 */
export interface Attack extends Timestamps {
  id: string;
  scan_id: string;
  finding_id?: string;
  attack_type: string;
  attack_vector: string;
  success_probability: number; // 0-1
  impact_score: number; // 0-10
  mitre_technique?: string;
  mitre_tactic?: string;
  attack_path: string[];
  impact_description?: string;
  prerequisites: string[];
  mitigation?: string;
  metadata?: Metadata;
}

/**
 * Attack with detailed information
 */
export interface AttackDetail extends Attack {
  finding_type?: string;
  finding_severity?: string;
  exploitation_steps?: {
    step_number: number;
    description: string;
    difficulty: string;
  }[];
}

/**
 * List of attacks
 */
export type AttackList = PaginatedResponse<Attack>;

/**
 * Attack chain - Multiple attacks in sequence
 */
export interface AttackChain {
  id: string;
  name: string;
  description: string;
  attacks: Attack[];
  total_probability: number;
  total_impact: number;
}

/**
 * MITRE ATT&CK mapping
 */
export interface MitreTechnique {
  id: string;
  name: string;
  tactic: string;
  description: string;
  external_references?: string[];
}

/**
 * Attack statistics
 */
export interface AttackStats {
  total_attacks: number;
  high_probability: number; // > 0.75
  high_impact: number; // > 7.0
  most_common_tactic: string;
  most_common_technique: string;
}

/**
 * Attack for visualization
 */
export interface AttackNode {
  id: string;
  type: string;
  vector: string;
  probability: number;
  impact: number;
  x?: number;
  y?: number;
}

/**
 * Attack edge for graph
 */
export interface AttackEdge {
  source: string;
  target: string;
  label?: string;
}
