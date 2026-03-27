"""
Architecture diagram generator for the Academic Conference Paper Submission System.
Creates a PNG diagram showing all system components and their relationships.

Student: Srinidhi Vutkoori (X25173243)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def generate_architecture_diagram():
    """
    Generate a system architecture diagram as a PNG file.
    Shows the three-tier architecture with React frontend, Flask backend,
    and six AWS cloud services.
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Title
    ax.text(8, 10.5, 'Academic Conference Paper Submission System',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='#1a237e')
    ax.text(8, 10.1, 'Srinidhi Vutkoori (X25173243) - Cloud Platform Programming',
            ha='center', va='center', fontsize=10, color='#666')

    # --- User Layer ---
    user_box = mpatches.FancyBboxPatch((6.5, 9.0), 3, 0.8,
                                         boxstyle="round,pad=0.1",
                                         facecolor='#e8eaf6', edgecolor='#1a237e', linewidth=2)
    ax.add_patch(user_box)
    ax.text(8, 9.4, 'Users (Authors / Reviewers / Organizers)',
            ha='center', va='center', fontsize=9, fontweight='bold')

    # Arrow from user to frontend
    ax.annotate('', xy=(8, 8.6), xytext=(8, 9.0),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))

    # --- Frontend Layer ---
    fe_box = mpatches.FancyBboxPatch((5.5, 7.8), 5, 0.8,
                                       boxstyle="round,pad=0.1",
                                       facecolor='#e3f2fd', edgecolor='#1565c0', linewidth=2)
    ax.add_patch(fe_box)
    ax.text(8, 8.3, 'React Frontend (Port 3000)', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#1565c0')
    ax.text(8, 8.0, 'Dashboard | Conferences | Papers | Reviews | Authors | AWS Status',
            ha='center', va='center', fontsize=7, color='#555')

    # Arrow from frontend to backend
    ax.annotate('', xy=(8, 7.0), xytext=(8, 7.8),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))
    ax.text(8.3, 7.4, 'REST API', ha='left', va='center', fontsize=7, color='#888')

    # --- Backend Layer ---
    be_box = mpatches.FancyBboxPatch((4, 5.8), 8, 1.2,
                                       boxstyle="round,pad=0.1",
                                       facecolor='#fff3e0', edgecolor='#e65100', linewidth=2)
    ax.add_patch(be_box)
    ax.text(8, 6.7, 'Flask Backend (Port 5000)', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#e65100')
    ax.text(8, 6.35, 'Routes: conferences | papers | reviews | authors | aws_status',
            ha='center', va='center', fontsize=7, color='#555')
    ax.text(8, 6.05, 'Services: DynamoDB | S3 | SES | Comprehend | CloudFront | Lambda',
            ha='center', va='center', fontsize=7, color='#555')

    # --- PaperFlow Library ---
    lib_box = mpatches.FancyBboxPatch((0.5, 5.8), 3, 1.2,
                                        boxstyle="round,pad=0.1",
                                        facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=2)
    ax.add_patch(lib_box)
    ax.text(2, 6.7, 'PaperFlow Library', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#7b1fa2')
    ax.text(2, 6.3, 'Paper | Reviewer\nConference | Submission\nScoring',
            ha='center', va='center', fontsize=7, color='#555')

    # Arrow from backend to library
    ax.annotate('', xy=(3.5, 6.4), xytext=(4, 6.4),
                arrowprops=dict(arrowstyle='->', color='#7b1fa2', lw=1.5))

    # --- Database Layer ---
    db_box = mpatches.FancyBboxPatch((0.5, 4.2), 3, 0.9,
                                       boxstyle="round,pad=0.1",
                                       facecolor='#e8f5e9', edgecolor='#2e7d32', linewidth=2)
    ax.add_patch(db_box)
    ax.text(2, 4.75, 'SQLite (Dev) / DynamoDB (Prod)', ha='center', va='center',
            fontsize=8, fontweight='bold', color='#2e7d32')
    ax.text(2, 4.45, 'Conferences | Papers | Reviews | Authors',
            ha='center', va='center', fontsize=7, color='#555')

    # Arrow from backend to DB
    ax.annotate('', xy=(2, 5.1), xytext=(5, 5.8),
                arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5))

    # --- AWS Services ---
    aws_title_y = 4.8
    ax.text(10, aws_title_y, 'AWS Cloud Services', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#e65100')

    services = [
        ('Amazon DynamoDB', '#e8f5e9', '#2e7d32', 'NoSQL Data Store'),
        ('Amazon S3', '#e3f2fd', '#1565c0', 'Paper PDF Storage'),
        ('Amazon SES', '#fce4ec', '#c62828', 'Email Notifications'),
        ('Amazon Comprehend', '#f3e5f5', '#7b1fa2', 'NLP Analysis'),
        ('Amazon CloudFront', '#fff3e0', '#e65100', 'CDN Distribution'),
        ('AWS Lambda', '#e0f7fa', '#00695c', 'Async Processing'),
    ]

    for i, (name, bg, edge, desc) in enumerate(services):
        col = i % 3
        row = i // 3
        x = 5.5 + col * 3.3
        y = 3.6 - row * 1.5

        svc_box = mpatches.FancyBboxPatch((x, y), 2.8, 1.1,
                                            boxstyle="round,pad=0.08",
                                            facecolor=bg, edgecolor=edge, linewidth=1.5)
        ax.add_patch(svc_box)
        ax.text(x + 1.4, y + 0.7, name, ha='center', va='center',
                fontsize=8, fontweight='bold', color=edge)
        ax.text(x + 1.4, y + 0.35, desc, ha='center', va='center',
                fontsize=6.5, color='#555')

    # Arrows from backend to AWS services
    for i in range(3):
        x_target = 5.5 + i * 3.3 + 1.4
        ax.annotate('', xy=(x_target, 4.7), xytext=(8, 5.8),
                    arrowprops=dict(arrowstyle='->', color='#999', lw=1, linestyle='dashed'))

    for i in range(3):
        x_target = 5.5 + i * 3.3 + 1.4
        ax.annotate('', xy=(x_target, 3.2), xytext=(8, 5.8),
                    arrowprops=dict(arrowstyle='->', color='#999', lw=1, linestyle='dashed'))

    # --- CI/CD note ---
    ax.text(2, 0.8, 'CI/CD: GitHub Actions', ha='center', va='center',
            fontsize=8, fontweight='bold', color='#333',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f5f5', edgecolor='#999'))
    ax.text(2, 0.4, 'Test Library -> Deploy Backend -> Deploy Frontend',
            ha='center', va='center', fontsize=7, color='#666')

    plt.tight_layout()
    output_path = 'architecture.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f'Architecture diagram saved to {output_path}')
    return output_path


if __name__ == '__main__':
    generate_architecture_diagram()
