from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sklearn.cluster import DBSCAN


@dataclass
class ClusterResult:
    cluster_id: int
    latitude: float
    longitude: float
    num_points: int


def cluster_incidents(
    coordinates: List[Tuple[float, float]],
    eps_km: float = 1.0,
    min_samples: int = 3,
) -> List[ClusterResult]:
    """
    Cluster incident coordinates using DBSCAN.

    Args:
        coordinates: List of (lat, lon) pairs.
        eps_km: Neighbourhood radius in kilometers.
        min_samples: Minimum points required to form a dense region.
    """
    if not coordinates:
        return []

    coords = np.array(coordinates)

    # Convert degrees to radians for haversine metric.
    radians = np.radians(coords)
    kms_per_radian = 6371.0088
    eps = eps_km / kms_per_radian

    db = DBSCAN(eps=eps, min_samples=min_samples, metric="haversine").fit(radians)
    labels = db.labels_

    clusters: List[ClusterResult] = []
    for cluster_id in set(labels):
        if cluster_id == -1:
            # Noise
            continue
        mask = labels == cluster_id
        cluster_points = coords[mask]
        lat_mean, lon_mean = cluster_points.mean(axis=0)
        clusters.append(
            ClusterResult(
                cluster_id=int(cluster_id),
                latitude=float(lat_mean),
                longitude=float(lon_mean),
                num_points=int(mask.sum()),
            )
        )

    return clusters

