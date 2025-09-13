"""
Script to run controlled experiments varying parameters.
"""

import os
import json
import itertools
from typing import List, Dict, Any
import time

from src.generate import generate_asset_sync
from src.metrics import compute_metrics, compare_meshes


def run_parameter_experiments(
    output_dir: str = "outputs/experiments",
    base_prompt: str = "test shape"
) -> Dict[str, Any]:
    """
    Run experiments varying different parameters.
    
    Args:
        output_dir: Output directory for experiments
        base_prompt: Base prompt for generation
    
    Returns:
        Dictionary with experiment results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Define parameter ranges
    seeds = [42, 123, 456]
    steps = [10, 20, 30]
    guidance_scales = [5.0, 7.5, 10.0]
    
    # Generate all combinations
    parameter_combinations = list(itertools.product(seeds, steps, guidance_scales))
    
    print(f"Running {len(parameter_combinations)} experiments...")
    
    results = []
    base_metrics = None
    
    for i, (seed, steps_val, guidance_scale) in enumerate(parameter_combinations):
        print(f"Experiment {i+1}/{len(parameter_combinations)}: seed={seed}, steps={steps_val}, guidance={guidance_scale}")
        
        try:
            # Generate asset
            result = generate_asset_sync(
                prompt=base_prompt,
                seed=seed,
                steps=steps_val,
                guidance_scale=guidance_scale,
                output_dir=output_dir
            )
            
            # Store base metrics for comparison
            if base_metrics is None:
                base_metrics = result["metrics"]
            
            # Compare with base
            comparison = compare_meshes(base_metrics, result["metrics"])
            
            experiment_result = {
                "experiment_id": i + 1,
                "parameters": {
                    "seed": seed,
                    "steps": steps_val,
                    "guidance_scale": guidance_scale
                },
                "result": result,
                "comparison": comparison,
                "timestamp": time.time()
            }
            
            results.append(experiment_result)
            
            # Save individual experiment
            exp_file = os.path.join(output_dir, f"experiment_{i+1:03d}.json")
            with open(exp_file, 'w') as f:
                json.dump(experiment_result, f, indent=2)
            
        except Exception as e:
            print(f"Experiment {i+1} failed: {e}")
            results.append({
                "experiment_id": i + 1,
                "parameters": {
                    "seed": seed,
                    "steps": steps_val,
                    "guidance_scale": guidance_scale
                },
                "error": str(e),
                "timestamp": time.time()
            })
    
    # Save summary
    summary = {
        "total_experiments": len(parameter_combinations),
        "successful_experiments": len([r for r in results if "error" not in r]),
        "failed_experiments": len([r for r in results if "error" in r]),
        "parameter_ranges": {
            "seeds": seeds,
            "steps": steps,
            "guidance_scales": guidance_scales
        },
        "results": results,
        "timestamp": time.time()
    }
    
    summary_file = os.path.join(output_dir, "experiments_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary


def analyze_experiments(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze experiment results and generate insights.
    
    Args:
        summary: Experiment summary
    
    Returns:
        Analysis results
    """
    successful_results = [r for r in summary["results"] if "error" not in r]
    
    if not successful_results:
        return {"error": "No successful experiments to analyze"}
    
    analysis = {
        "parameter_effects": {},
        "quality_metrics": {},
        "recommendations": []
    }
    
    # Analyze parameter effects
    seeds = {}
    steps = {}
    guidance_scales = {}
    
    for result in successful_results:
        params = result["parameters"]
        metrics = result["result"]["metrics"]
        
        # Group by parameter
        seed = params["seed"]
        if seed not in seeds:
            seeds[seed] = []
        seeds[seed].append(metrics)
        
        step = params["steps"]
        if step not in steps:
            steps[step] = []
        steps[step].append(metrics)
        
        guidance = params["guidance_scale"]
        if guidance not in guidance_scales:
            guidance_scales[guidance] = []
        guidance_scales[guidance].append(metrics)
    
    # Analyze effects
    analysis["parameter_effects"]["seed"] = analyze_parameter_effect(seeds, "seed")
    analysis["parameter_effects"]["steps"] = analyze_parameter_effect(steps, "steps")
    analysis["parameter_effects"]["guidance_scale"] = analyze_parameter_effect(guidance_scales, "guidance_scale")
    
    # Quality analysis
    all_metrics = [r["result"]["metrics"] for r in successful_results]
    analysis["quality_metrics"] = analyze_quality_metrics(all_metrics)
    
    # Generate recommendations
    analysis["recommendations"] = generate_recommendations(analysis)
    
    return analysis


def analyze_parameter_effect(parameter_groups: Dict, param_name: str) -> Dict[str, Any]:
    """Analyze the effect of a single parameter."""
    import numpy as np
    
    effects = {}
    
    for param_value, metrics_list in parameter_groups.items():
        if not metrics_list:
            continue
        
        # Calculate statistics for this parameter value
        vertex_counts = [m["vertex_count"] for m in metrics_list]
        face_counts = [m["face_count"] for m in metrics_list]
        volumes = [m["volume"] for m in metrics_list]
        file_sizes = [m["file_size_bytes"] for m in metrics_list]
        
        effects[param_value] = {
            "vertex_count": {
                "mean": float(np.mean(vertex_counts)),
                "std": float(np.std(vertex_counts)),
                "min": int(np.min(vertex_counts)),
                "max": int(np.max(vertex_counts))
            },
            "face_count": {
                "mean": float(np.mean(face_counts)),
                "std": float(np.std(face_counts)),
                "min": int(np.min(face_counts)),
                "max": int(np.max(face_counts))
            },
            "volume": {
                "mean": float(np.mean(volumes)),
                "std": float(np.std(volumes)),
                "min": float(np.min(volumes)),
                "max": float(np.max(volumes))
            },
            "file_size": {
                "mean": float(np.mean(file_sizes)),
                "std": float(np.std(file_sizes)),
                "min": int(np.min(file_sizes)),
                "max": int(np.max(file_sizes))
            }
        }
    
    return effects


def analyze_quality_metrics(all_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze quality metrics across all experiments."""
    import numpy as np
    
    quality = {
        "loadability_rate": sum(1 for m in all_metrics if m["loadable"]) / len(all_metrics),
        "watertight_rate": sum(1 for m in all_metrics if m["is_watertight"]) / len(all_metrics),
        "uv_coverage_rate": sum(1 for m in all_metrics if m["has_uv_coordinates"]) / len(all_metrics),
        "average_vertex_count": float(np.mean([m["vertex_count"] for m in all_metrics])),
        "average_face_count": float(np.mean([m["face_count"] for m in all_metrics])),
        "average_file_size_mb": float(np.mean([m["file_size_mb"] for m in all_metrics]))
    }
    
    return quality


def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analysis."""
    recommendations = []
    
    quality = analysis["quality_metrics"]
    
    if quality["loadability_rate"] < 0.9:
        recommendations.append("Improve mesh generation to increase loadability rate")
    
    if quality["watertight_rate"] < 0.5:
        recommendations.append("Consider improving mesh topology for better watertightness")
    
    if quality["average_file_size_mb"] > 1.0:
        recommendations.append("Consider implementing better mesh compression")
    
    if quality["average_vertex_count"] > 10000:
        recommendations.append("Consider reducing mesh complexity for better performance")
    
    return recommendations


if __name__ == "__main__":
    print("Running parameter experiments...")
    
    # Run experiments
    summary = run_parameter_experiments()
    
    print(f"Completed {summary['successful_experiments']}/{summary['total_experiments']} experiments")
    
    # Analyze results
    analysis = analyze_experiments(summary)
    
    # Save analysis
    analysis_file = "outputs/experiments/analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print("Analysis saved to outputs/experiments/analysis.json")
    print("Recommendations:")
    for rec in analysis.get("recommendations", []):
        print(f"- {rec}")
